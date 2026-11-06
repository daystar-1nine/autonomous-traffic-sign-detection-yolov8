package com.autonomous.aicontrol.controller

/**
 * Real-time diagnostic telemetry state for Cosmic Byte Ares Pro and virtual controls.
 */
data class GamepadDiagnosticData(
    val isConnected: Boolean = false,
    val deviceName: String = "No Gamepad Connected",
    val vendorId: Int = 0,
    val productId: Int = 0,
    val leftStickX: Float = 0f,
    val leftStickY: Float = 0f,
    val rightStickX: Float = 0f,
    val rightStickY: Float = 0f,
    val leftTrigger: Float = 0f,
    val rightTrigger: Float = 0f,
    val dpadX: Float = 0f,
    val dpadY: Float = 0f,
    val activeButtons: Set<String> = emptySet(),
    val leftMotorPwm: Int = 0,
    val rightMotorPwm: Int = 0,
    val speedProfileName: String = "NORMAL",
    val speedProfileMaxPwm: Int = 750
)
