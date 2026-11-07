package com.autonomous.aicontrol.decision

import com.autonomous.aicontrol.ai.DetectionResult
import kotlin.math.max

enum class VehicleState {
    CRUISING,
    TURNING,
    POST_TURN_CRUISE,
    STOPPED,
    MANUAL,
    EMERGENCY_STOP
}

data class DrivingDecision(
    val state: VehicleState,
    val command: String, // FORWARD, BACKWARD, LEFT, RIGHT, STOP
    val speed: Int,
    val targetSignName: String,
    val proximityPercent: Float,
    val distanceZone: String, // CLEAR, FAR, APPROACHING, ACTION_ZONE
    val statusMessage: String
)

class DecisionEngine(
    var defaultCruiseSpeed: Int = 700,
    var turnSpeed: Int = 850,
    var turnExecutionDurationMs: Long = 650L,   // Active 90-degree pivot turn duration
    var postTurnCruiseDurationMs: Long = 1500L, // Mandatory forward driving after turn
    var turnCooldownMs: Long = 3000L,           // Ignore same turn sign to prevent re-spinning
    var stopHoldDurationMs: Long = 3000L
) {
    private var state = VehicleState.CRUISING
    private var stateStartTime = System.currentTimeMillis()

    // Turn Execution & Cooldown Tracking
    private var activeTurnCommand = "FORWARD"
    private var turnStartTime = 0L
    private var postTurnStartTime = 0L
    private var turnCooldownUntil = 0L
    private var lastTurnSignName: String = ""

    // Detection smoothing & persistence
    private var consecutiveCount = 0
    private var lastCandidateName: String? = null
    private var lastConfirmedSign: DetectionResult? = null
    private var lastSignTimestamp = 0L
    private val SIGN_PERSISTENCE_MS = 350L

    private val THRESH_ACTION_ZONE = 0.05f
    private val THRESH_APPROACH = 0.03f

    fun processDetections(detections: List<DetectionResult>, manualOverride: Boolean): DrivingDecision {
        val now = System.currentTimeMillis()

        if (manualOverride) {
            state = VehicleState.MANUAL
            consecutiveCount = 0
            lastCandidateName = null
            lastConfirmedSign = null
            return DrivingDecision(
                state = VehicleState.MANUAL,
                command = "STOP",
                speed = 0,
                targetSignName = "MANUAL OVERRIDE",
                proximityPercent = 0f,
                distanceZone = "MANUAL",
                statusMessage = "MANUAL CONTROLLER ACTIVE"
            )
        }

        // 1. Pick primary detection with highest confidence
        val primary = detections.maxByOrNull { it.confidence }

        val detectedSign: DetectionResult? = if (primary != null) {
            if (primary.className == lastCandidateName) {
                consecutiveCount++
            } else {
                consecutiveCount = 1
                lastCandidateName = primary.className
            }
            lastConfirmedSign = primary
            lastSignTimestamp = now
            primary
        } else if (lastConfirmedSign != null && (now - lastSignTimestamp < SIGN_PERSISTENCE_MS)) {
            // Smooth over single-frame dropped detections to eliminate HUD/motor flicker
            lastConfirmedSign
        } else {
            consecutiveCount = max(0, consecutiveCount - 1)
            if (consecutiveCount == 0) {
                lastCandidateName = null
                lastConfirmedSign = null
            }
            null
        }

        // Calculate Proximity Metrics
        var proximityPct = 0f
        var distanceZone = "CLEAR"
        if (detectedSign != null) {
            proximityPct = (detectedSign.heightRatio / 0.20f * 100f).coerceIn(0f, 100f)
            distanceZone = when {
                detectedSign.heightRatio >= THRESH_ACTION_ZONE -> "ACTION_ZONE"
                detectedSign.heightRatio >= THRESH_APPROACH -> "APPROACHING"
                else -> "FAR_DETECTED"
            }
        }

        // 2. CRITICAL SAFETY HAZARDS (STOP / NO ENTRY / DEAD END)
        // Hazards ALWAYS take priority over any in-progress turn or cruise!
        if (detectedSign != null) {
            val confPct = (detectedSign.confidence * 100).toInt()
            if (detectedSign.className == "stop") {
                state = VehicleState.STOPPED
                stateStartTime = now
                return DrivingDecision(
                    state = VehicleState.STOPPED,
                    command = "STOP",
                    speed = 0,
                    targetSignName = "stop",
                    proximityPercent = proximityPct,
                    distanceZone = distanceZone,
                    statusMessage = "STOP SIGN DETECTED ($confPct%) -> BRAKING"
                )
            }
            if (detectedSign.className == "no_entry" || detectedSign.className == "dead_end") {
                state = VehicleState.STOPPED
                stateStartTime = now
                return DrivingDecision(
                    state = VehicleState.STOPPED,
                    command = "STOP",
                    speed = 0,
                    targetSignName = detectedSign.className,
                    proximityPercent = proximityPct,
                    distanceZone = distanceZone,
                    statusMessage = "HAZARD (${detectedSign.className.uppercase()} $confPct%) -> STOP"
                )
            }
        }

        // 3. ACTIVE TURN MANEUVER IN PROGRESS
        // If the car is currently executing a 90-degree turn, complete the timed turn arc!
        if (state == VehicleState.TURNING) {
            val elapsedTurn = now - turnStartTime
            if (elapsedTurn < turnExecutionDurationMs) {
                val remainMs = turnExecutionDurationMs - elapsedTurn
                return DrivingDecision(
                    state = VehicleState.TURNING,
                    command = activeTurnCommand,
                    speed = turnSpeed,
                    targetSignName = lastTurnSignName,
                    proximityPercent = proximityPct,
                    distanceZone = "TURNING",
                    statusMessage = "EXECUTING $activeTurnCommand TURN [${remainMs}ms remain]"
                )
            } else {
                // Turn duration has elapsed! 90-degree pivot is COMPLETE!
                // Transition immediately to POST_TURN_CRUISE (drive straight ahead!)
                state = VehicleState.POST_TURN_CRUISE
                postTurnStartTime = now
                turnCooldownUntil = now + turnCooldownMs
            }
        }

        // 4. POST-TURN CRUISE PHASE (MANDATORY STRAIGHT DRIVING)
        // Drive straight forward into the new lane/corridor
        if (state == VehicleState.POST_TURN_CRUISE) {
            val elapsedPost = now - postTurnStartTime
            if (elapsedPost < postTurnCruiseDurationMs) {
                return DrivingDecision(
                    state = VehicleState.POST_TURN_CRUISE,
                    command = "FORWARD",
                    speed = defaultCruiseSpeed,
                    targetSignName = "post_turn_cruise",
                    proximityPercent = 0f,
                    distanceZone = "POST_TURN",
                    statusMessage = "TURN FINISHED -> ACCELERATING STRAIGHT"
                )
            } else {
                state = VehicleState.CRUISING
            }
        }

        // 5. DIRECTIONAL TURN SIGN HANDLING (WITH COOLDOWN REFRACTORY LOCKOUT)
        if (detectedSign != null) {
            val confPct = (detectedSign.confidence * 100).toInt()
            when (detectedSign.className) {
                "right_turn", "left_turn" -> {
                    // Check if we are in the cooldown refractory period
                    if (now < turnCooldownUntil) {
                        // We recently completed a turn and are driving past the sign!
                        // SUPPRESS RE-TRIGGERING so the car doesn't spin in circles!
                        val remSec = ((turnCooldownUntil - now) / 100L) / 10.0f
                        return DrivingDecision(
                            state = VehicleState.CRUISING,
                            command = "FORWARD",
                            speed = defaultCruiseSpeed,
                            targetSignName = detectedSign.className,
                            proximityPercent = proximityPct,
                            distanceZone = "COOLDOWN",
                            statusMessage = "TURN SIGN LOCKED (${remSec}s COOLDOWN) -> CRUISING STRAIGHT"
                        )
                    } else {
                        // Cooldown has expired, trigger NEW turn maneuver!
                        state = VehicleState.TURNING
                        turnStartTime = now
                        activeTurnCommand = if (detectedSign.className == "left_turn") "LEFT" else "RIGHT"
                        lastTurnSignName = detectedSign.className
                        turnCooldownUntil = now + turnCooldownMs

                        return DrivingDecision(
                            state = VehicleState.TURNING,
                            command = activeTurnCommand,
                            speed = turnSpeed,
                            targetSignName = detectedSign.className,
                            proximityPercent = proximityPct,
                            distanceZone = distanceZone,
                            statusMessage = "SIGN DETECTED: $activeTurnCommand TURN ($confPct%) -> INITIATING TURN"
                        )
                    }
                }

                "straight_ahead" -> {
                    state = VehicleState.CRUISING
                    return DrivingDecision(
                        state = VehicleState.CRUISING,
                        command = "FORWARD",
                        speed = defaultCruiseSpeed,
                        targetSignName = "straight_ahead",
                        proximityPercent = proximityPct,
                        distanceZone = distanceZone,
                        statusMessage = "STRAIGHT SIGN ($confPct%) -> CRUISING"
                    )
                }
            }
        }

        // 6. STOPPED STATE HOLD (Holding the line at a stop sign)
        if (state == VehicleState.STOPPED && (now - stateStartTime < stopHoldDurationMs)) {
            val remainSec = ((stopHoldDurationMs - (now - stateStartTime)) / 100f).toInt() / 10f
            return DrivingDecision(
                state = VehicleState.STOPPED,
                command = "STOP",
                speed = 0,
                targetSignName = "stop_hold",
                proximityPercent = 0f,
                distanceZone = "HOLD",
                statusMessage = "HOLDING STOP LINE (${remainSec}s)"
            )
        }

        // 7. DEFAULT: CLEAR ROADWAY -> CRUISE FORWARD SAFELY
        state = VehicleState.CRUISING
        return DrivingDecision(
            state = VehicleState.CRUISING,
            command = "FORWARD",
            speed = defaultCruiseSpeed,
            targetSignName = "none",
            proximityPercent = 0f,
            distanceZone = "CLEAR",
            statusMessage = "PATH CLEAR -> CRUISING"
        )
    }

    fun emergencyStop(): DrivingDecision {
        state = VehicleState.EMERGENCY_STOP
        return DrivingDecision(
            state = VehicleState.EMERGENCY_STOP,
            command = "STOP",
            speed = 0,
            targetSignName = "EMERGENCY_STOP",
            proximityPercent = 100f,
            distanceZone = "LOCKED",
            statusMessage = "EMERGENCY STOP ENGAGED"
        )
    }

    fun reset() {
        state = VehicleState.CRUISING
        consecutiveCount = 0
        lastCandidateName = null
        lastConfirmedSign = null
        turnStartTime = 0L
        postTurnStartTime = 0L
        turnCooldownUntil = 0L
    }
}
