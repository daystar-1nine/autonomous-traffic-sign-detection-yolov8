package com.autonomous.aicontrol.decision

import com.autonomous.aicontrol.ai.DetectionResult
import kotlin.math.abs
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
    private val turnSpeed: Int = 760,
    private val turnDurationMs: Long = 850L,
    private val stopHoldDurationMs: Long = 3000L
) {
    private var state = VehicleState.CRUISING
    private var stateStartTime = System.currentTimeMillis()
    private var activeCommand = "FORWARD"
    private var cooldownUntil = 0L

    // Temporal Debouncing & Tracking
    private var lastCandidateName: String? = null
    private var consecutiveCount = 0
    private val REQUIRED_FRAMES = 2

    // Proximity Thresholds (Height of Bounding Box / Frame Height)
    private val THRESH_ACTION_ZONE = 0.07f
    private val THRESH_APPROACH = 0.04f

    fun processDetections(detections: List<DetectionResult>, manualOverride: Boolean): DrivingDecision {
        val now = System.currentTimeMillis()

        if (manualOverride) {
            state = VehicleState.MANUAL
            return DrivingDecision(
                state = VehicleState.MANUAL,
                command = "STOP",
                speed = 0,
                targetSignName = "MANUAL OVERRIDE",
                proximityPercent = 0f,
                distanceZone = "MANUAL",
                statusMessage = "MANUAL KEYBOARD/UI OVERRIDE ACTIVE"
            )
        }

        // Primary candidate is largest bounding box
        val primary = detections.maxByOrNull { it.areaRatio }

        // Temporal Debounce: Confirm detection consistency
        val confirmedSign: DetectionResult? = if (primary != null) {
            if (primary.className == lastCandidateName) {
                consecutiveCount++
            } else {
                consecutiveCount = 1
                lastCandidateName = primary.className
            }
            if (consecutiveCount >= REQUIRED_FRAMES) primary else null
        } else {
            consecutiveCount = max(0, consecutiveCount - 1)
            if (consecutiveCount == 0) lastCandidateName = null
            null
        }

        val elapsedInState = now - stateStartTime

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

        // ---------------- STATE MACHINE TRANSITIONS ----------------
        when (state) {
            VehicleState.TURNING -> {
                // Maneuver Lock: Complete calibrated turning arc
                if (elapsedInState >= turnDurationMs) {
                    state = VehicleState.CRUISING
                    stateStartTime = now
                    activeCommand = "FORWARD"
                    cooldownUntil = now + 2500L // 2.5s cooldown against duplicate turns
                } else {
                    return DrivingDecision(
                        state = VehicleState.TURNING,
                        command = activeCommand,
                        speed = turnSpeed,
                        targetSignName = confirmedSign?.className ?: "TURNING",
                        proximityPercent = proximityPct,
                        distanceZone = distanceZone,
                        statusMessage = "EXECUTING $activeCommand TURN"
                    )
                }
            }

            VehicleState.STOPPED -> {
                // Regulatory Stop Line Hold
                if (elapsedInState >= stopHoldDurationMs) {
                    state = VehicleState.CRUISING
                    stateStartTime = now
                    activeCommand = "FORWARD"
                    cooldownUntil = now + 3000L // 3.0s cooldown to clear intersection
                } else {
                    val remainingSec = ((stopHoldDurationMs - elapsedInState) / 100f).toInt() / 10f
                    return DrivingDecision(
                        state = VehicleState.STOPPED,
                        command = "STOP",
                        speed = 0,
                        targetSignName = "stop",
                        proximityPercent = proximityPct,
                        distanceZone = distanceZone,
                        statusMessage = "HOLDING REGULATORY STOP (${remainingSec}s)"
                    )
                }
            }

            VehicleState.CRUISING -> {
                val inCooldown = now < cooldownUntil

                if (confirmedSign != null && !inCooldown) {
                    val hRatio = confirmedSign.heightRatio

                    when (confirmedSign.className) {
                        "stop" -> {
                            if (hRatio >= THRESH_ACTION_ZONE) {
                                state = VehicleState.STOPPED
                                stateStartTime = now
                                activeCommand = "STOP"
                                return DrivingDecision(
                                    state = VehicleState.STOPPED,
                                    command = "STOP",
                                    speed = 0,
                                    targetSignName = "stop",
                                    proximityPercent = proximityPct,
                                    distanceZone = distanceZone,
                                    statusMessage = "STOPPING AT REGULATORY LINE"
                                )
                            } else {
                                // Smooth approach deceleration
                                activeCommand = "FORWARD"
                                return DrivingDecision(
                                    state = VehicleState.CRUISING,
                                    command = "FORWARD",
                                    speed = 480,
                                    targetSignName = "stop",
                                    proximityPercent = proximityPct,
                                    distanceZone = distanceZone,
                                    statusMessage = "DECELERATING (STOP SIGN AHEAD)"
                                )
                            }
                        }

                        "no_entry", "dead_end" -> {
                            if (hRatio >= 0.10f) {
                                state = VehicleState.STOPPED
                                stateStartTime = now
                                activeCommand = "STOP"
                                return DrivingDecision(
                                    state = VehicleState.STOPPED,
                                    command = "STOP",
                                    speed = 0,
                                    targetSignName = confirmedSign.className,
                                    proximityPercent = proximityPct,
                                    distanceZone = distanceZone,
                                    statusMessage = "EMERGENCY BRAKE (${confirmedSign.className.uppercase()})"
                                )
                            }
                        }

                        "left_turn" -> {
                            if (hRatio >= THRESH_ACTION_ZONE) {
                                state = VehicleState.TURNING
                                stateStartTime = now
                                activeCommand = "LEFT"
                                return DrivingDecision(
                                    state = VehicleState.TURNING,
                                    command = "LEFT",
                                    speed = turnSpeed,
                                    targetSignName = "left_turn",
                                    proximityPercent = proximityPct,
                                    distanceZone = distanceZone,
                                    statusMessage = "TURNING LEFT"
                                )
                            } else {
                                activeCommand = "FORWARD"
                                return DrivingDecision(
                                    state = VehicleState.CRUISING,
                                    command = "FORWARD",
                                    speed = 520,
                                    targetSignName = "left_turn",
                                    proximityPercent = proximityPct,
                                    distanceZone = distanceZone,
                                    statusMessage = "APPROACHING LEFT TURN"
                                )
                            }
                        }

                        "right_turn" -> {
                            if (hRatio >= THRESH_ACTION_ZONE) {
                                state = VehicleState.TURNING
                                stateStartTime = now
                                activeCommand = "RIGHT"
                                return DrivingDecision(
                                    state = VehicleState.TURNING,
                                    command = "RIGHT",
                                    speed = turnSpeed,
                                    targetSignName = "right_turn",
                                    proximityPercent = proximityPct,
                                    distanceZone = distanceZone,
                                    statusMessage = "TURNING RIGHT"
                                )
                            } else {
                                activeCommand = "FORWARD"
                                return DrivingDecision(
                                    state = VehicleState.CRUISING,
                                    command = "FORWARD",
                                    speed = 520,
                                    targetSignName = "right_turn",
                                    proximityPercent = proximityPct,
                                    distanceZone = distanceZone,
                                    statusMessage = "APPROACHING RIGHT TURN"
                                )
                            }
                        }

                        "straight_ahead" -> {
                            activeCommand = "FORWARD"
                            return DrivingDecision(
                                state = VehicleState.CRUISING,
                                command = "FORWARD",
                                speed = defaultCruiseSpeed,
                                targetSignName = "straight_ahead",
                                proximityPercent = proximityPct,
                                distanceZone = distanceZone,
                                statusMessage = "CRUISING (PATH CLEAR)"
                            )
                        }
                    }
                }
            }

            else -> {}
        }

        // Default: Maintain normal cruise
        return DrivingDecision(
            state = VehicleState.CRUISING,
            command = "FORWARD",
            speed = defaultCruiseSpeed,
            targetSignName = confirmedSign?.className ?: "None",
            proximityPercent = proximityPct,
            distanceZone = distanceZone,
            statusMessage = "CRUISING FORWARD"
        )
    }

    fun emergencyStop(): DrivingDecision {
        state = VehicleState.EMERGENCY_STOP
        activeCommand = "STOP"
        return DrivingDecision(
            state = VehicleState.EMERGENCY_STOP,
            command = "STOP",
            speed = 0,
            targetSignName = "EMERGENCY_STOP",
            proximityPercent = 0f,
            distanceZone = "SAFETY_LOCK",
            statusMessage = "EMERGENCY ZERO-SPEED BRAKE ENGAGED"
        )
    }
}
