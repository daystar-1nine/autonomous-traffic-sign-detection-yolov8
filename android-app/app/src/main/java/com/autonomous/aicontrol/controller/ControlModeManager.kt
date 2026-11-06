package com.autonomous.aicontrol.controller

enum class ControlMode {
    MANUAL,
    AUTONOMOUS,
    EMERGENCY_STOP
}

interface ControlModeListener {
    fun onModeChanged(oldMode: ControlMode, newMode: ControlMode, reason: String)
    fun onEmergencyStopTriggered(source: String)
    fun onEmergencyStopReset()
}

class ControlModeManager(
    private val listener: ControlModeListener? = null
) {
    @Volatile
    var currentMode: ControlMode = ControlMode.EMERGENCY_STOP // Safe default on boot
        private set

    private var previousMode: ControlMode = ControlMode.MANUAL
    private var isEmergencyStopActive = true

    /**
     * Attempts to transition to MANUAL mode.
     * @param hasConnectedController True if Ares Pro or valid controller is detected.
     * @return True if transition succeeded, false if blocked.
     */
    @Synchronized
    fun setManualMode(hasConnectedController: Boolean = true, reason: String = "User Selected"): Boolean {
        if (isEmergencyStopActive) {
            // Cannot switch while emergency stop is locked
            return false
        }
        if (currentMode == ControlMode.MANUAL) return true

        val old = currentMode
        currentMode = ControlMode.MANUAL
        previousMode = old
        listener?.onModeChanged(old, currentMode, reason)
        return true
    }

    /**
     * Attempts to transition to AUTONOMOUS mode.
     * @param isCameraReady True if CameraX pipeline and neural detector are initialized.
     * @return True if transition succeeded, false if blocked.
     */
    @Synchronized
    fun setAutonomousMode(isCameraReady: Boolean = true, reason: String = "User Selected"): Boolean {
        if (isEmergencyStopActive) {
            return false
        }
        if (!isCameraReady) {
            return false
        }
        if (currentMode == ControlMode.AUTONOMOUS) return true

        val old = currentMode
        currentMode = ControlMode.AUTONOMOUS
        previousMode = old
        listener?.onModeChanged(old, currentMode, reason)
        return true
    }

    /**
     * Triggers global Emergency Stop. Immediately locks the vehicle in STOP state.
     */
    @Synchronized
    fun triggerEmergencyStop(source: String = "Global E-Stop"): ControlMode {
        val old = currentMode
        isEmergencyStopActive = true
        currentMode = ControlMode.EMERGENCY_STOP
        listener?.onEmergencyStopTriggered(source)
        listener?.onModeChanged(old, currentMode, "EMERGENCY STOP: $source")
        return currentMode
    }

    /**
     * Explicitly resets the Emergency Stop state and unlocks the vehicle.
     * Restores to the safe requested mode (defaults to MANUAL).
     */
    @Synchronized
    fun resetEmergencyStop(targetMode: ControlMode = ControlMode.MANUAL): Boolean {
        if (!isEmergencyStopActive) return true

        isEmergencyStopActive = false
        val old = currentMode
        currentMode = targetMode
        listener?.onEmergencyStopReset()
        listener?.onModeChanged(old, currentMode, "E-Stop Reset -> $targetMode")
        return true
    }

    /**
     * Failsafe: Handles controller disconnection.
     * If currently in MANUAL mode, immediately halts vehicle and engages Emergency Stop.
     */
    @Synchronized
    fun handleControllerDisconnected(): Boolean {
        if (currentMode == ControlMode.MANUAL) {
            triggerEmergencyStop("Ares Pro Controller Disconnected in Manual Mode")
            return true
        }
        return false
    }

    fun isManual(): Boolean = (currentMode == ControlMode.MANUAL) && !isEmergencyStopActive
    fun isAutonomous(): Boolean = (currentMode == ControlMode.AUTONOMOUS) && !isEmergencyStopActive
    fun isEmergencyStop(): Boolean = isEmergencyStopActive || (currentMode == ControlMode.EMERGENCY_STOP)
}
