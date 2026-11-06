package com.autonomous.aicontrol.controller

import android.content.Context
import android.hardware.input.InputManager
import android.view.InputDevice
import android.view.KeyEvent
import android.view.MotionEvent
import kotlin.math.abs

enum class ControllerButtonAction {
    ENABLE_MANUAL,
    ENABLE_AUTONOMOUS,
    TOGGLE_AUTONOMOUS_RUN,
    EMERGENCY_STOP,
    CYCLE_SPEED_PROFILE,
    DECREASE_SPEED,
    INCREASE_SPEED,
    TOGGLE_CRUISE_CONTROL
}

interface ControllerEventListener {
    fun onJoystickMoved(axisX: Float, axisY: Float)
    fun onControllerInput(
        axisX: Float,
        axisY: Float,
        rightTrigger: Float,
        leftTrigger: Float,
        turboBoost: Boolean
    )
    fun onButtonActionTriggered(action: ControllerButtonAction)
    fun onControllerConnectionChanged(connected: Boolean, deviceName: String)
    fun onDiagnosticsUpdated(diagnosticData: GamepadDiagnosticData)
}

class AresProController(
    private val context: Context,
    private val listener: ControllerEventListener? = null
) : InputManager.InputDeviceListener {

    private val inputManager = context.getSystemService(Context.INPUT_SERVICE) as InputManager
    var connectedDeviceId: Int = -1
        private set
    var connectedDeviceName: String = "Disconnected"
        private set

    // Axes
    var leftStickX: Float = 0f
        private set
    var leftStickY: Float = 0f
        private set
    var rightStickX: Float = 0f
        private set
    var rightStickY: Float = 0f
        private set
    var leftTrigger: Float = 0f
        private set
    var rightTrigger: Float = 0f
        private set
    var dpadX: Float = 0f
        private set
    var dpadY: Float = 0f
        private set

    val pressedButtons = mutableSetOf<String>()

    // Configurable Deadband Threshold
    var deadbandThreshold: Float = 0.05f

    // Configurable Keycode Mapping
    var keycodeManualMode: Int = KeyEvent.KEYCODE_BUTTON_A
    var keycodeAutonomousMode: Int = KeyEvent.KEYCODE_BUTTON_B
    var keycodeEmergencyStop: Int = KeyEvent.KEYCODE_BUTTON_X
    var keycodeCruiseControl: Int = KeyEvent.KEYCODE_BUTTON_Y
    var keycodeSpeedProfileCycle: Int = KeyEvent.KEYCODE_BUTTON_L1
    var keycodeTurboBoost: Int = KeyEvent.KEYCODE_BUTTON_R1
    var keycodeStartButton: Int = KeyEvent.KEYCODE_BUTTON_START
    var keycodeSelectButton: Int = KeyEvent.KEYCODE_BUTTON_SELECT

    init {
        inputManager.registerInputDeviceListener(this, null)
        detectConnectedGamepad()
    }

    fun detectConnectedGamepad() {
        val deviceIds = inputManager.inputDeviceIds
        for (id in deviceIds) {
            val device = inputManager.getInputDevice(id) ?: continue
            val sources = device.sources
            if ((sources and InputDevice.SOURCE_GAMEPAD) == InputDevice.SOURCE_GAMEPAD ||
                (sources and InputDevice.SOURCE_JOYSTICK) == InputDevice.SOURCE_JOYSTICK
            ) {
                connectedDeviceId = id
                connectedDeviceName = device.name ?: "Cosmic Byte Ares Pro"
                listener?.onControllerConnectionChanged(true, connectedDeviceName)
                broadcastDiagnostics()
                return
            }
        }
        connectedDeviceId = -1
        connectedDeviceName = "Disconnected"
        listener?.onControllerConnectionChanged(false, connectedDeviceName)
        broadcastDiagnostics()
    }

    fun isConnected(): Boolean = connectedDeviceId != -1

    /**
     * Handles analog joystick and trigger motion events from the controller.
     */
    fun handleMotionEvent(event: MotionEvent): Boolean {
        if ((event.source and InputDevice.SOURCE_JOYSTICK) == InputDevice.SOURCE_JOYSTICK ||
            (event.source and InputDevice.SOURCE_GAMEPAD) == InputDevice.SOURCE_GAMEPAD
        ) {
            if (connectedDeviceId == -1) {
                connectedDeviceId = event.deviceId
                val dev = event.device
                connectedDeviceName = dev?.name ?: "Cosmic Byte Ares Pro"
                listener?.onControllerConnectionChanged(true, connectedDeviceName)
            }

            // Left Stick (Steering X & Arcade Throttle Y)
            val rawX = event.getAxisValue(MotionEvent.AXIS_X)
            val rawY = event.getAxisValue(MotionEvent.AXIS_Y)
            leftStickX = applyDeadband(rawX)
            leftStickY = applyDeadband(rawY)

            // Right Stick (Camera or Auxiliary)
            val rawZ = event.getAxisValue(MotionEvent.AXIS_Z)
            val rawRZ = event.getAxisValue(MotionEvent.AXIS_RZ)
            rightStickX = applyDeadband(if (rawZ != 0f) rawZ else event.getAxisValue(MotionEvent.AXIS_RX))
            rightStickY = applyDeadband(if (rawRZ != 0f) rawRZ else event.getAxisValue(MotionEvent.AXIS_RY))

            // Pressure Sensitive Triggers: RT (Gas/Forward) & LT (Brake/Reverse)
            val rawRt = maxOf(
                event.getAxisValue(MotionEvent.AXIS_RTRIGGER),
                event.getAxisValue(MotionEvent.AXIS_GAS),
                if (event.getAxisValue(MotionEvent.AXIS_RZ) > 0f) event.getAxisValue(MotionEvent.AXIS_RZ) else 0f
            ).coerceIn(0f, 1f)

            val rawLt = maxOf(
                event.getAxisValue(MotionEvent.AXIS_LTRIGGER),
                event.getAxisValue(MotionEvent.AXIS_BRAKE),
                if (event.getAxisValue(MotionEvent.AXIS_Z) > 0f) event.getAxisValue(MotionEvent.AXIS_Z) else 0f
            ).coerceIn(0f, 1f)

            rightTrigger = applyDeadband(rawRt)
            leftTrigger = applyDeadband(rawLt)

            // D-Pad Hat
            dpadX = event.getAxisValue(MotionEvent.AXIS_HAT_X)
            dpadY = event.getAxisValue(MotionEvent.AXIS_HAT_Y)

            val isTurbo = pressedButtons.contains("R1") || pressedButtons.contains("RB")

            listener?.onControllerInput(leftStickX, leftStickY, rightTrigger, leftTrigger, isTurbo)
            listener?.onJoystickMoved(leftStickX, leftStickY)
            broadcastDiagnostics()
            return true
        }
        return false
    }

    /**
     * Handles button key down events.
     */
    fun handleKeyDown(keyCode: Int, event: KeyEvent): Boolean {
        if (!isGamepadEvent(event)) return false

        val buttonName = KeyEvent.keyCodeToString(keyCode).removePrefix("KEYCODE_BUTTON_")
        pressedButtons.add(buttonName)

        when (keyCode) {
            keycodeEmergencyStop -> {
                listener?.onButtonActionTriggered(ControllerButtonAction.EMERGENCY_STOP)
            }
            keycodeManualMode -> {
                listener?.onButtonActionTriggered(ControllerButtonAction.ENABLE_MANUAL)
            }
            keycodeAutonomousMode -> {
                listener?.onButtonActionTriggered(ControllerButtonAction.ENABLE_AUTONOMOUS)
            }
            keycodeStartButton, KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE, KeyEvent.KEYCODE_MEDIA_PLAY, KeyEvent.KEYCODE_BUTTON_MODE -> {
                listener?.onButtonActionTriggered(ControllerButtonAction.TOGGLE_AUTONOMOUS_RUN)
            }
            keycodeCruiseControl -> {
                listener?.onButtonActionTriggered(ControllerButtonAction.TOGGLE_CRUISE_CONTROL)
            }
            keycodeSpeedProfileCycle, keycodeSelectButton -> {
                listener?.onButtonActionTriggered(ControllerButtonAction.CYCLE_SPEED_PROFILE)
            }
            keycodeTurboBoost -> {
                // Handled via pressedButtons + onControllerInput
                val isTurbo = true
                listener?.onControllerInput(leftStickX, leftStickY, rightTrigger, leftTrigger, isTurbo)
            }
        }

        broadcastDiagnostics()
        return true
    }

    /**
     * Handles button key up events.
     */
    fun handleKeyUp(keyCode: Int, event: KeyEvent): Boolean {
        if (!isGamepadEvent(event)) return false
        val buttonName = KeyEvent.keyCodeToString(keyCode).removePrefix("KEYCODE_BUTTON_")
        pressedButtons.remove(buttonName)

        if (keyCode == keycodeTurboBoost) {
            listener?.onControllerInput(leftStickX, leftStickY, rightTrigger, leftTrigger, false)
        }

        broadcastDiagnostics()
        return true
    }

    fun isGamepadEvent(event: KeyEvent): Boolean {
        val source = event.source
        val isControllerSource = ((source and InputDevice.SOURCE_GAMEPAD) == InputDevice.SOURCE_GAMEPAD ||
                (source and InputDevice.SOURCE_JOYSTICK) == InputDevice.SOURCE_JOYSTICK)

        return isControllerSource ||
                KeyEvent.isGamepadButton(event.keyCode) ||
                event.keyCode == KeyEvent.KEYCODE_BUTTON_START ||
                event.keyCode == KeyEvent.KEYCODE_BUTTON_SELECT ||
                event.keyCode == KeyEvent.KEYCODE_BUTTON_MODE ||
                event.keyCode == KeyEvent.KEYCODE_BUTTON_A ||
                event.keyCode == KeyEvent.KEYCODE_BUTTON_B ||
                event.keyCode == KeyEvent.KEYCODE_BUTTON_X ||
                event.keyCode == KeyEvent.KEYCODE_BUTTON_Y ||
                event.keyCode == KeyEvent.KEYCODE_BUTTON_L1 ||
                event.keyCode == KeyEvent.KEYCODE_BUTTON_R1 ||
                event.keyCode == KeyEvent.KEYCODE_BUTTON_L2 ||
                event.keyCode == KeyEvent.KEYCODE_BUTTON_R2 ||
                event.keyCode == KeyEvent.KEYCODE_BUTTON_THUMBL ||
                event.keyCode == KeyEvent.KEYCODE_BUTTON_THUMBR ||
                event.keyCode == KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE ||
                event.keyCode == KeyEvent.KEYCODE_MEDIA_PLAY
    }

    private fun applyDeadband(value: Float): Float {
        val magnitude = abs(value)
        if (magnitude < deadbandThreshold) return 0f
        val normalized = (magnitude - deadbandThreshold) / (1.0f - deadbandThreshold)
        return if (value < 0) -normalized else normalized
    }

    private fun broadcastDiagnostics() {
        val dev = if (connectedDeviceId != -1) inputManager.getInputDevice(connectedDeviceId) else null
        val data = GamepadDiagnosticData(
            isConnected = connectedDeviceId != -1,
            deviceName = connectedDeviceName,
            vendorId = dev?.vendorId ?: 0,
            productId = dev?.productId ?: 0,
            leftStickX = leftStickX,
            leftStickY = leftStickY,
            rightStickX = rightStickX,
            rightStickY = rightStickY,
            leftTrigger = leftTrigger,
            rightTrigger = rightTrigger,
            activeButtons = pressedButtons.toSet()
        )
        listener?.onDiagnosticsUpdated(data)
    }

    override fun onInputDeviceAdded(deviceId: Int) {
        detectConnectedGamepad()
    }

    override fun onInputDeviceRemoved(deviceId: Int) {
        detectConnectedGamepad()
    }

    override fun onInputDeviceChanged(deviceId: Int) {
        detectConnectedGamepad()
    }

    fun release() {
        inputManager.unregisterInputDeviceListener(this)
    }
}
