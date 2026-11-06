package com.autonomous.aicontrol.controller

import kotlin.math.abs
import kotlin.math.max
import kotlin.math.min
import kotlin.math.sign

enum class SpeedProfile(val displayName: String, val maxPwm: Int, val maxTurnPwm: Int) {
    ECO("ECO (50%)", 500, 420),
    NORMAL("NORMAL (75%)", 750, 620),
    SPORT("SPORT (100%)", 1000, 850)
}

data class MotorOutputs(
    val leftPwm: Int,
    val rightPwm: Int,
    val targetLeftPwm: Int,
    val targetRightPwm: Int
)

class DifferentialDriveController(
    var currentProfile: SpeedProfile = SpeedProfile.NORMAL
) {
    // Current Output PWM (smoothed & rate-limited)
    var currentLeftPwm: Int = 0
        private set
    var currentRightPwm: Int = 0
        private set

    // Independent Motor Hardware Trim Factors (e.g., 1.0 = 100%, 0.95 = 95%)
    var leftTrimFactor: Float = 1.00f
    var rightTrimFactor: Float = 1.00f

    // Acceleration & Deceleration Slew Rates (PWM delta per update tick, ~30-50Hz)
    var accelSlewRate: Int = 85   // Smooth progressive acceleration
    var decelSlewRate: Int = 180  // Fast, responsive deceleration

    // S-Curve Exponential Smoothing Weight (0.0 = no filter, 1.0 = frozen)
    var inputSmoothingAlpha: Float = 0.25f
    private var smoothedThrottle: Float = 0f
    private var smoothedSteering: Float = 0f

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

    /**
     * Computes differential drive motor outputs from raw joystick inputs.
     * @param stickX Left joystick X-axis [-1.0 to 1.0], positive = right turn
     * @param stickY Left joystick Y-axis [-1.0 to 1.0], negative = forward in Android
     * @return MotorOutputs containing left and right motor PWM values [-1023 to +1023]
     */
    fun computeMotorOutputs(stickX: Float, stickY: Float): MotorOutputs {
        // 1. Invert Android Y axis so forward is positive
        val rawThrottle = -stickY
        val rawSteering = stickX

        // 2. Exponential Input Smoothing
        smoothedThrottle += inputSmoothingAlpha * (rawThrottle - smoothedThrottle)
        smoothedSteering += inputSmoothingAlpha * (rawSteering - smoothedSteering)

        // If inputs are near zero, clamp immediately to zero to avoid slow creep
        val activeThrottle = if (abs(smoothedThrottle) < 0.03f) 0f else smoothedThrottle
        val activeSteering = if (abs(smoothedSteering) < 0.03f) 0f else smoothedSteering

        // 3. Raw Differential Calculations
        val leftRaw = activeThrottle + activeSteering
        val rightRaw = activeThrottle - activeSteering

        // 4. Normalization across Max Magnitude to prevent saturation during turning while accelerating
        val maxMag = max(1.0f, max(abs(leftRaw), abs(rightRaw)))
        val normalizedLeft = leftRaw / maxMag
        val normalizedRight = rightRaw / maxMag

        // 5. Scale to Active Speed Profile Max PWM & Apply Independent Hardware Trims
        val targetLeft = (normalizedLeft * currentProfile.maxPwm * leftTrimFactor)
            .toInt().coerceIn(-currentProfile.maxPwm, currentProfile.maxPwm)
        val targetRight = (normalizedRight * currentProfile.maxPwm * rightTrimFactor)
            .toInt().coerceIn(-currentProfile.maxPwm, currentProfile.maxPwm)

        // 6. Slew-Rate Limiting (Acceleration & Deceleration Ramping) with Zero-Crossing Safety
        currentLeftPwm = rampPwm(currentLeftPwm, targetLeft)
        currentRightPwm = rampPwm(currentRightPwm, targetRight)

        return MotorOutputs(
            leftPwm = currentLeftPwm,
            rightPwm = currentRightPwm,
            targetLeftPwm = targetLeft,
            targetRightPwm = targetRight
        )
    }

    /**
     * Ramps the current PWM towards the target PWM using independent accel/decel slew rates.
     * Implements zero-crossing deceleration: when direction inverts, it ramps down to 0 first.
     */
    private fun rampPwm(current: Int, target: Int): Int {
        if (current == target) return target

        // Direction Reversal Check (e.g. forward to backward or vice-versa)
        if (current != 0 && target != 0 && sign(current.toFloat()) != sign(target.toFloat())) {
            // Rapidly ramp down towards zero before crossing zero
            val step = decelSlewRate
            return if (current > 0) max(0, current - step) else min(0, current + step)
        }

        val isAccelerating = abs(target) > abs(current)
        val step = if (isAccelerating) accelSlewRate else decelSlewRate

        return if (target > current) {
            min(target, current + step)
        } else {
            max(target, current - step)
        }
    }

    /**
     * Immediately resets all motor outputs to zero (Emergency Stop / Mode Switch).
     */
    fun reset() {
        currentLeftPwm = 0
        currentRightPwm = 0
        smoothedThrottle = 0f
        smoothedSteering = 0f
    }
}
