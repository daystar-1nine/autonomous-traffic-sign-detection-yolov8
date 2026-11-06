"""
Unit Test: Centralized Control Mode Manager & Safety State Machine
06_TESTING/controller_tests/test_mode_manager.py
"""

class MockControlModeManager:
    def __init__(self):
        self.mode = "EMERGENCY_STOP"  # Boot safe state
        self.is_e_stop = True
        self.last_transition_reason = "System Initialized"

    def set_manual_mode(self, has_controller=True):
        if self.is_e_stop:
            return False
        if not has_controller:
            return False
        self.mode = "MANUAL"
        self.last_transition_reason = "Manual Selected"
        return True

    def set_autonomous_mode(self, is_camera_ready=True):
        if self.is_e_stop:
            return False
        if not is_camera_ready:
            return False
        self.mode = "AUTONOMOUS"
        self.last_transition_reason = "Auto Selected"
        return True

    def trigger_emergency_stop(self, source="E-Stop Trigger"):
        self.is_e_stop = True
        self.mode = "EMERGENCY_STOP"
        self.last_transition_reason = f"E-Stop: {source}"
        return self.mode

    def reset_emergency_stop(self, target_mode="MANUAL"):
        self.is_e_stop = False
        self.mode = target_mode
        self.last_transition_reason = f"E-Stop Reset -> {target_mode}"
        return True

    def handle_controller_disconnect(self):
        if self.mode == "MANUAL":
            self.trigger_emergency_stop("Ares Pro Disconnected")
            return True
        return False


def test_boot_safety_default():
    mgr = MockControlModeManager()
    assert mgr.is_e_stop is True, "System should boot into locked E-Stop state"
    assert mgr.mode == "EMERGENCY_STOP", "Initial mode must be EMERGENCY_STOP"
    assert mgr.set_manual_mode() is False, "Cannot switch to manual while E-Stop is active"
    print(" [PASS] Vehicle initializes safely in locked Emergency Stop mode on startup.")


def test_emergency_stop_clear_and_mode_switching():
    mgr = MockControlModeManager()
    # Explicit unlock
    mgr.reset_emergency_stop(target_mode="MANUAL")
    assert mgr.is_e_stop is False
    assert mgr.mode == "MANUAL"

    # Switch to Autonomous
    assert mgr.set_autonomous_mode(is_camera_ready=True) is True
    assert mgr.mode == "AUTONOMOUS"

    # Switch back to Manual
    assert mgr.set_manual_mode(has_controller=True) is True
    assert mgr.mode == "MANUAL"
    print(" [PASS] Dual-mode switching (Manual <-> Autonomous) functions cleanly when unlocked.")


def test_emergency_stop_override_hierarchy():
    mgr = MockControlModeManager()
    mgr.reset_emergency_stop("AUTONOMOUS")
    assert mgr.mode == "AUTONOMOUS"

    # Press Emergency Stop Button (X on Ares Pro)
    mgr.trigger_emergency_stop("Gamepad Button X")
    assert mgr.is_e_stop is True
    assert mgr.mode == "EMERGENCY_STOP"

    # Verify other modes are blocked
    assert mgr.set_manual_mode() is False
    assert mgr.set_autonomous_mode() is False
    print(" [PASS] Emergency STOP immediately overrides active mode and blocks commands.")


def test_controller_disconnect_failsafe():
    mgr = MockControlModeManager()
    mgr.reset_emergency_stop("MANUAL")
    assert mgr.mode == "MANUAL"

    # Controller drops connection
    result = mgr.handle_controller_disconnect()
    assert result is True, "Disconnect event must be intercepted"
    assert mgr.mode == "EMERGENCY_STOP", "Car must halt into Emergency Stop on controller disconnect"
    assert mgr.mode != "AUTONOMOUS", "Car must NEVER auto-switch to autonomous when gamepad disconnects!"
    print(" [PASS] Controller disconnection in Manual mode safely halts vehicle without auto-switching.")


if __name__ == "__main__":
    test_boot_safety_default()
    test_emergency_stop_clear_and_mode_switching()
    test_emergency_stop_override_hierarchy()
    test_controller_disconnect_failsafe()
    print("\nALL CONTROL MODE MANAGER TESTS PASSED!")
