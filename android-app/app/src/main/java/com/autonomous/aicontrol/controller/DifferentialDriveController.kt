package com.autonomous.aicontrol.controller

import kotlin.math.abs
import kotlin.math.max
import kotlin.math.min
import kotlin.math.sign

enum class SpeedProfile(val displayName: String, val maxPwm: Int, val minKickPwm: Int) {
    ECO("ECO (60%)", 650, 380),
    NORMAL("NORMAL (85%)", 880, 420),
    SPORT("SPORT (100%)", 1023, 460)
}

data class MotorOutputs(
    val leftPwm: Int,
    val rightPwm: Int,
    val targetLeftPwm: Int,
    val targetRightPwm: Int,
    val throttlePercent: Int = 0,
    val isTurboActive: Boolean = false,
    val isAebActive: Boolean = false
)

class DifferentialDriveController(
    var currentProfile: SpeedProfile = SpeedProfile.SPORT
) {
    // Current Output PWM (smoothed & rate-limited)
    var currentLeftPwm: Int = 0
        private set
    var currentRightPwm: Int = 0
        private set

    // Independent Motor Hardware Trim Factors (e.g., 1.0 = 100%, 0.95 = 95%)
    var leftTrimFactor: Float = 1.00f
    var rightTrimFactor: Float = 1.00f

    // Highly responsive Slew Rates (PWM delta per update tick ~30-50Hz)
    var accelSlewRate: Int = 220  // Rapid, punchy acceleration
    var decelSlewRate: Int = 450  // Instant crisp braking

    // Fast Input Smoothing Alpha (0.70 = snappy instant controller feel)
    var inputSmoothingAlpha: Float = 0.70f
    private var smoothedThrottle: Float = 0f
    private var smoothedSteering: Float = 0f

    // Cruise control support
    var isCruiseControlActive: Boolean = false
        private set
    var cruisePwm: Int = 0
        private set

    fun cycleSpeedProfile(): SpeedProfile {
        val profiles = SpeedProfile.values()
        val nextIdx = (currentProfile.ordinal + 1) % profiles.size
        currentProfile = profiles[nextIdx]
        return currentProfile
    }

    fun setSpeedProfileByIndex(index: Int): SpeedProfile {
        val profiles = SpeedProfile.values()
        currentProfile = profiles[index.coerceIn(0, profiles.size - 1)]
        return currentProfile
    }

    fun toggleCruiseControl(): Boolean {
        isCruiseControlActive = !isCruiseControlActive
        if (isCruiseControlActive) {
            cruisePwm = max(abs(currentLeftPwm), abs(currentRightPwm))
            if (cruisePwm < currentProfile.minKickPwm) {
                cruisePwm = (currentProfile.minKickPwm + currentProfile.maxPwm) / 2
            }
        }
        return isCruiseControlActive
    }

    fun cancelCruiseControl() {
        isCruiseControlActive = false
        cruisePwm = 0
    }

    /**
     * Overload for legacy callers using stick only.
     */
    fun computeMotorOutputs(stickX: Float, stickY: Float): MotorOutputs {
        return computeMotorOutputs(stickX, stickY, 0f, 0f, false, false)
    }

    /**
     * Primary High-Performance Differential Steering & Throttle Computation.
     * Supports:
     * - RT (Right Trigger): Analog Forward Throttle (pressure-sensitive 0.0 to 1.0)
     * - LT (Left Trigger) : Analog Reverse / Brake (pressure-sensitive 0.0 to 1.0)
     * - Left Stick X      : Steering [-1.0 (Left) to +1.0 (Right)]
     * - Turbo Boost       : Max PWM (1023) with instant slew
     * - AEB Override      : Instant collision brake
     */
    fun computeMotorOutputs(
        stickX: Float,
        stickY: Float,
        rightTrigger: Float = 0f,
        leftTrigger: Float = 0f,
        turboBoost: Boolean = false,
        emergencyBrakeOverride: Boolean = false
    ): MotorOutputs {
        // 1. If Emergency Brake Override / AEB is active, force instant stop
        if (emergencyBrakeOverride) {
            currentLeftPwm = 0
            currentRightPwm = 0
            smoothedThrottle = 0f
            smoothedSteering = 0f
            cancelCruiseControl()
            return MotorOutputs(0, 0, 0, 0, 0, isTurboActive = false, isAebActive = true)
        }

        // 2. Determine Raw Throttle
        // Priority: RT / LT triggers take precedence; fallback to stick Y
        val triggerThrottle = rightTrigger - leftTrigger
        val rawThrottle = if (abs(triggerThrottle) > 0.03f) {
            cancelCruiseControl()
            triggerThrottle
        } else if (isCruiseControlActive) {
            (cruisePwm.toFloat() / currentProfile.maxPwm.toFloat())
        } else {
            -stickY // Android stick Y is negative upwards
        }

        val rawSteering = stickX

        // 3. Exponential Input Smoothing
        smoothedThrottle += inputSmoothingAlpha * (rawThrottle - smoothedThrottle)
        smoothedSteering += inputSmoothingAlpha * (rawSteering - smoothedSteering)

        val activeThrottle = if (abs(smoothedThrottle) < 0.02f) 0f else smoothedThrottle
        val activeSteering = if (abs(smoothedSteering) < 0.02f) 0f else smoothedSteering

        // 4. Differential Steering Mixing
        // Left wheel = Throttle + Steering; Right wheel = Throttle - Steering
        var leftRaw = activeThrottle + activeSteering
        var rightRaw = activeThrottle - activeSteering

        // Stationary Pivot Turn: If throttle is near zero and steering is active
        if (abs(activeThrottle) < 0.03f && abs(activeSteering) >= 0.03f) {
            leftRaw = activeSteering
            rightRaw = -activeSteering
        }

        val maxMag = max(1.0f, max(abs(leftRaw), abs(rightRaw)))
        val normLeft = leftRaw / maxMag
        val normRight = rightRaw / maxMag

        // 5. Active Max & Kick PWM Calculation (Overcomes TT Gearbox Friction)
        val activeMaxPwm = if (turboBoost) 1023 else currentProfile.maxPwm
        val activeMinPwm = if (turboBoost) 500 else currentProfile.minKickPwm

        // Dynamic Scaling: map magnitude from [minKick .. maxPwm] for instant torque
        fun applyTorqueCurve(normVal: Float): Int {
            val mag = abs(normVal)
            if (mag <= 0.03f) return 0
            val scaled = activeMinPwm + (activeMaxPwm - activeMinPwm) * ((mag - 0.03f) / 0.97f)
            val pwm = scaled.toInt().coerceIn(0, activeMaxPwm)
            return if (normVal >= 0) pwm else -pwm
        }

        val targetLeft = (applyTorqueCurve(normLeft) * leftTrimFactor).toInt().coerceIn(-activeMaxPwm, activeMaxPwm)
        val targetRight = (applyTorqueCurve(normRight) * rightTrimFactor).toInt().coerceIn(-activeMaxPwm, activeMaxPwm)

        // 6. Slew-Rate Limiting with Turbo Bypass
        val activeAccelStep = if (turboBoost) 1023 else accelSlewRate
        val activeDecelStep = if (turboBoost) 1023 else decelSlewRate

        currentLeftPwm = rampPwm(currentLeftPwm, targetLeft, activeAccelStep, activeDecelStep)
        currentRightPwm = rampPwm(currentRightPwm, targetRight, activeAccelStep, activeDecelStep)

        val throttlePct = ((abs(activeThrottle)) * 100).toInt().coerceIn(0, 100)

        return MotorOutputs(
            leftPwm = currentLeftPwm,
            rightPwm = currentRightPwm,
            targetLeftPwm = targetLeft,
            targetRightPwm = targetRight,
            throttlePercent = throttlePct,
            isTurboActive = turboBoost,
            isAebActive = false
        )
    }

    private fun rampPwm(current: Int, target: Int, accelStep: Int, decelStep: Int): Int {
        if (current == target) return target

        // Zero-Crossing Reversal Protection: Decelerate to 0 before inverting direction
        if (current != 0 && target != 0 && sign(current.toFloat()) != sign(target.toFloat())) {
            return if (current > 0) max(0, current - decelStep) else min(0, current + decelStep)
        }

        val isAccelerating = abs(target) > abs(current)
        val step = if (isAccelerating) accelStep else decelStep

        return if (target > current) {
            min(target, current + step)
        } else {
            max(target, current - step)
        }
    }

    fun reset() {
        currentLeftPwm = 0
        currentRightPwm = 0
        smoothedThrottle = 0f
        smoothedSteering = 0f
        cancelCruiseControl()
    }
}
