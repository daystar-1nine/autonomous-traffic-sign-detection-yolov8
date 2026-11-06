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
    EMERGENCY_STOP,
    CYCLE_SPEED_PROFILE,
    DECREASE_SPEED,
    INCREASE_SPEED
}

interface ControllerEventListener {
    fun onJoystickMoved(axisX: Float, axisY: Float)
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

    private val pressedButtons = mutableSetOf<String>()

    // Configurable Deadband Threshold
    var deadbandThreshold: Float = 0.10f

    // Configurable Keycode Mapping
    var keycodeManualMode: Int = KeyEvent.KEYCODE_BUTTON_A
    var keycodeAutonomousMode: Int = KeyEvent.KEYCODE_BUTTON_B
    var keycodeEmergencyStop: Int = KeyEvent.KEYCODE_BUTTON_X
    var keycodeCycleProfile: Int = KeyEvent.KEYCODE_BUTTON_Y
    var keycodeSpeedDown: Int = KeyEvent.KEYCODE_BUTTON_L1
    var keycodeSpeedUp: Int = KeyEvent.KEYCODE_BUTTON_R1

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
                connectedDeviceName = device.name ?: "Wireless Gamepad"
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
            // Update device ID if newly detected
            if (connectedDeviceId == -1) {
                connectedDeviceId = event.deviceId
                val dev = event.device
                connectedDeviceName = dev?.name ?: "Cosmic Byte Ares Pro"
                listener?.onControllerConnectionChanged(true, connectedDeviceName)
            }

            // Left Stick
            val rawX = event.getAxisValue(MotionEvent.AXIS_X)
            val rawY = event.getAxisValue(MotionEvent.AXIS_Y)
            leftStickX = applyDeadband(rawX)
            leftStickY = applyDeadband(rawY)

            // Right Stick (Z / RZ or RX / RY depending on Android driver)
            val rawZ = event.getAxisValue(MotionEvent.AXIS_Z)
            val rawRZ = event.getAxisValue(MotionEvent.AXIS_RZ)
            rightStickX = applyDeadband(if (rawZ != 0f) rawZ else event.getAxisValue(MotionEvent.AXIS_RX))
            rightStickY = applyDeadband(if (rawRZ != 0f) rawRZ else event.getAxisValue(MotionEvent.AXIS_RY))

            // Triggers
            leftTrigger = event.getAxisValue(MotionEvent.AXIS_LTRIGGER).coerceAtLeast(event.getAxisValue(MotionEvent.AXIS_BRAKE))
            rightTrigger = event.getAxisValue(MotionEvent.AXIS_RTRIGGER).coerceAtLeast(event.getAxisValue(MotionEvent.AXIS_GAS))

            // D-Pad Hat
            dpadX = event.getAxisValue(MotionEvent.AXIS_HAT_X)
            dpadY = event.getAxisValue(MotionEvent.AXIS_HAT_Y)

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
            keycodeCycleProfile -> {
                listener?.onButtonActionTriggered(ControllerButtonAction.CYCLE_SPEED_PROFILE)
            }
            keycodeSpeedDown -> {
                listener?.onButtonActionTriggered(ControllerButtonAction.DECREASE_SPEED)
            }
            keycodeSpeedUp -> {
                listener?.onButtonActionTriggered(ControllerButtonAction.INCREASE_SPEED)
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
        broadcastDiagnostics()
        return true
    }

    private fun isGamepadEvent(event: KeyEvent): Boolean {
        val source = event.source
        return ((source and InputDevice.SOURCE_GAMEPAD) == InputDevice.SOURCE_GAMEPAD ||
                (source and InputDevice.SOURCE_JOYSTICK) == InputDevice.SOURCE_JOYSTICK ||
                KeyEvent.isGamepadButton(event.keyCode))
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
            dpadX = dpadX,
            dpadY = dpadY,
            activeButtons = pressedButtons.toSet()
        )
        listener?.onDiagnosticsUpdated(data)
    }

    // InputDeviceListener callbacks
    override fun onInputDeviceAdded(deviceId: Int) {
        val dev = inputManager.getInputDevice(deviceId) ?: return
        if ((dev.sources and InputDevice.SOURCE_GAMEPAD) == InputDevice.SOURCE_GAMEPAD ||
            (dev.sources and InputDevice.SOURCE_JOYSTICK) == InputDevice.SOURCE_JOYSTICK
        ) {
            connectedDeviceId = deviceId
            connectedDeviceName = dev.name ?: "Cosmic Byte Ares Pro"
            listener?.onControllerConnectionChanged(true, connectedDeviceName)
            broadcastDiagnostics()
        }
    }

    override fun onInputDeviceRemoved(deviceId: Int) {
        if (deviceId == connectedDeviceId) {
            connectedDeviceId = -1
            connectedDeviceName = "Disconnected"
            leftStickX = 0f
            leftStickY = 0f
            pressedButtons.clear()
            listener?.onControllerConnectionChanged(false, connectedDeviceName)
            broadcastDiagnostics()
        }
    }

    override fun onInputDeviceChanged(deviceId: Int) {
        if (deviceId == connectedDeviceId) {
            detectConnectedGamepad()
        }
    }

    fun release() {
        inputManager.unregisterInputDeviceListener(this)
    }
}
