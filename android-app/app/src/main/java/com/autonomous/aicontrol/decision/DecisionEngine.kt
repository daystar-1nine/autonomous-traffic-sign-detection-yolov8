package com.autonomous.aicontrol.decision

import com.autonomous.aicontrol.ai.DetectionResult
import kotlin.math.max

enum class VehicleState {
    CRUISING,
    TURNING,
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
    private val defaultCruiseSpeed: Int = 700,
    private val turnSpeed: Int = 850,
    private val turnHoldDurationMs: Long = 600L,
    private val stopHoldDurationMs: Long = 3000L
) {
    private var state = VehicleState.CRUISING
    private var stateStartTime = System.currentTimeMillis()
    private var lastTurnCommand = "FORWARD"
    private var lastTurnTimestamp = 0L

    private var consecutiveCount = 0
    private var lastCandidateName: String? = null

    private val THRESH_ACTION_ZONE = 0.05f
    private val THRESH_APPROACH = 0.03f

    fun processDetections(detections: List<DetectionResult>, manualOverride: Boolean): DrivingDecision {
        val now = System.currentTimeMillis()

        if (manualOverride) {
            state = VehicleState.MANUAL
            consecutiveCount = 0
            lastCandidateName = null
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

        val confirmedSign: DetectionResult? = if (primary != null) {
            if (primary.className == lastCandidateName) {
                consecutiveCount++
            } else {
                consecutiveCount = 1
                lastCandidateName = primary.className
            }
            primary
        } else {
            consecutiveCount = max(0, consecutiveCount - 1)
            if (consecutiveCount == 0) lastCandidateName = null
            null
        }

        // Calculate Proximity Metrics
        var proximityPct = 0f
        var distanceZone = "CLEAR"
        if (confirmedSign != null) {
            proximityPct = (confirmedSign.heightRatio / 0.20f * 100f).coerceIn(0f, 100f)
            distanceZone = when {
                confirmedSign.heightRatio >= THRESH_ACTION_ZONE -> "ACTION_ZONE"
                confirmedSign.heightRatio >= THRESH_APPROACH -> "APPROACHING"
                else -> "FAR_DETECTED"
            }
        }

        // 2. Active Maneuver Execution
        if (confirmedSign != null) {
            val confPct = (confirmedSign.confidence * 100).toInt()
            when (confirmedSign.className) {
                "stop" -> {
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

                "no_entry", "dead_end" -> {
                    state = VehicleState.STOPPED
                    stateStartTime = now
                    return DrivingDecision(
                        state = VehicleState.STOPPED,
                        command = "STOP",
                        speed = 0,
                        targetSignName = confirmedSign.className,
                        proximityPercent = proximityPct,
                        distanceZone = distanceZone,
                        statusMessage = "HAZARD (${confirmedSign.className.uppercase()} $confPct%) -> STOP"
                    )
                }

                "right_turn" -> {
                    state = VehicleState.TURNING
                    lastTurnCommand = "RIGHT"
                    lastTurnTimestamp = now
                    return DrivingDecision(
                        state = VehicleState.TURNING,
                        command = "RIGHT",
                        speed = turnSpeed,
                        targetSignName = "right_turn",
                        proximityPercent = proximityPct,
                        distanceZone = distanceZone,
                        statusMessage = "RIGHT TURN SIGN ($confPct%) -> TURNING RIGHT"
                    )
                }

                "left_turn" -> {
                    state = VehicleState.TURNING
                    lastTurnCommand = "LEFT"
                    lastTurnTimestamp = now
                    return DrivingDecision(
                        state = VehicleState.TURNING,
                        command = "LEFT",
                        speed = turnSpeed,
                        targetSignName = "left_turn",
                        proximityPercent = proximityPct,
                        distanceZone = distanceZone,
                        statusMessage = "LEFT TURN SIGN ($confPct%) -> TURNING LEFT"
                    )
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

        // 3. Fallback: If turn was recently triggered, finish turn arc smoothly
        if (state == VehicleState.TURNING && (now - lastTurnTimestamp < turnHoldDurationMs)) {
            return DrivingDecision(
                state = VehicleState.TURNING,
                command = lastTurnCommand,
                speed = turnSpeed,
                targetSignName = lastTurnCommand.lowercase() + "_turn",
                proximityPercent = 0f,
                distanceZone = "COMPLETING_TURN",
                statusMessage = "COMPLETING $lastTurnCommand TURN ARC"
            )
        }

        // If in STOPPED state, hold stop line for stopHoldDurationMs
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

        // Default: Path is clear, cruise forward safely
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
}
