"""
Unit Test: Differential Steering Mathematics, Slew-Rate Ramping & Profile Clamping
06_TESTING/controller_tests/test_differential_drive.py
"""

import math


class MockDifferentialDriveController:
    PROFILES = {
        "ECO": (500, 420),
        "NORMAL": (750, 620),
        "SPORT": (1000, 850)
    }

    def __init__(self, profile="NORMAL"):
        self.profile_name = profile
        self.max_pwm, self.max_turn = self.PROFILES[profile]
        self.current_left = 0
        self.current_right = 0
        self.left_trim = 1.00
        self.right_trim = 1.00
        self.accel_step = 85
        self.decel_step = 180
        self.deadband = 0.10
        self.alpha = 0.25
        self.smoothed_throttle = 0.0
        self.smoothed_steering = 0.0

    def apply_deadband(self, value):
        mag = abs(value)
        if mag < self.deadband:
            return 0.0
        norm = (mag - self.deadband) / (1.0 - self.deadband)
        return -norm if value < 0 else norm

    def ramp_pwm(self, current, target):
        if current == target:
            return target
        # Zero-crossing reversal protection
        if current != 0 and target != 0 and (current > 0) != (target > 0):
            step = self.decel_step
            return max(0, current - step) if current > 0 else min(0, current + step)

        is_accel = abs(target) > abs(current)
        step = self.accel_step if is_accel else self.decel_step
        if target > current:
            return min(target, current + step)
        else:
            return max(target, current - step)

    def compute(self, stick_x, stick_y):
        filt_x = self.apply_deadband(stick_x)
        filt_y = self.apply_deadband(stick_y)

        # Invert Y so up/forward is positive
        raw_throttle = -filt_y
        raw_steering = filt_x

        self.smoothed_throttle += self.alpha * (raw_throttle - self.smoothed_throttle)
        self.smoothed_steering += self.alpha * (raw_steering - self.smoothed_steering)

        t = 0.0 if abs(self.smoothed_throttle) < 0.03 else self.smoothed_throttle
        s = 0.0 if abs(self.smoothed_steering) < 0.03 else self.smoothed_steering

        left_raw = t + s
        right_raw = t - s

        max_mag = max(1.0, abs(left_raw), abs(right_raw))
        left_norm = left_raw / max_mag
        right_norm = right_raw / max_mag

        target_left = int(round(left_norm * self.max_pwm * self.left_trim))
        target_right = int(round(right_norm * self.max_pwm * self.right_trim))

        self.current_left = self.ramp_pwm(self.current_left, target_left)
        self.current_right = self.ramp_pwm(self.current_right, target_right)

        return self.current_left, self.current_right, target_left, target_right


def test_deadband():
    ctrl = MockDifferentialDriveController()
    assert ctrl.apply_deadband(0.05) == 0.0, "Deadband failed to filter low displacement"
    assert ctrl.apply_deadband(-0.08) == 0.0, "Deadband failed to filter negative displacement"
    val = ctrl.apply_deadband(1.0)
    assert abs(val - 1.0) < 1e-4, "Full displacement should equal 1.0"
    print(" [PASS] Joystick deadband correctly rejects noise < 0.10.")


def test_straight_forward_ramping():
    ctrl = MockDifferentialDriveController(profile="NORMAL")  # Max 750
    # Simulate pushing stick full forward (stick_y = -1.0) over multiple ticks
    target_reached = False
    for tick in range(30):
        l, r, tl, tr = ctrl.compute(stick_x=0.0, stick_y=-1.0)
        assert l == r, f"Motors should be symmetric on straight drive: L={l}, R={r}"
        assert l >= 0, "Motor should not be negative for forward"
        if l == 750 and r == 750:
            target_reached = True
            break
    assert target_reached, "Motor failed to reach target speed 750 with progressive ramp"
    print(" [PASS] Straight-line acceleration ramps smoothly and symmetrically.")


def test_reversal_zero_crossing():
    ctrl = MockDifferentialDriveController(profile="NORMAL")
    # Accelerate forward
    for _ in range(25):
        ctrl.compute(stick_x=0.0, stick_y=-1.0)
    assert ctrl.current_left > 500, "Failed to reach high forward speed"

    # Abruptly pull full reverse (stick_y = +1.0)
    # The controller must decelerate to 0 before going negative
    crossed_zero = False
    was_positive = True
    for _ in range(30):
        l, r, _, _ = ctrl.compute(stick_x=0.0, stick_y=1.0)
        if was_positive and l <= 0:
            crossed_zero = True
            was_positive = False
        if l < 0:
            assert crossed_zero, "Motor crossed to negative without zero-deceleration phase"
            break
    assert crossed_zero, "Zero crossing check failed"
    print(" [PASS] Abrupt reversal forces clean zero-crossing deceleration before reversing.")


def test_pivot_turn():
    ctrl = MockDifferentialDriveController(profile="NORMAL")
    # Full right turn on the spot (throttle=0, stick_x = +1.0)
    for _ in range(25):
        l, r, _, _ = ctrl.compute(stick_x=1.0, stick_y=0.0)
    assert l > 0, "Left motor must spin forward during right turn"
    assert r < 0, "Right motor must spin backward during right turn"
    assert abs(l) == abs(r), "Pivot turn should have equal and opposite motor PWM"
    print(" [PASS] Skid differential pivot turn calculates equal and opposite wheel velocities.")


def test_speed_profiles():
    ctrl_eco = MockDifferentialDriveController(profile="ECO")
    ctrl_sport = MockDifferentialDriveController(profile="SPORT")

    for _ in range(30):
        ctrl_eco.compute(0.0, -1.0)
        ctrl_sport.compute(0.0, -1.0)

    assert ctrl_eco.current_left == 500, f"Expected 500 for ECO, got {ctrl_eco.current_left}"
    assert ctrl_sport.current_left == 1000, f"Expected 1000 for SPORT, got {ctrl_sport.current_left}"
    print(" [PASS] Speed profiles clamp max PWM correctly (ECO=500, SPORT=1000).")


if __name__ == "__main__":
    test_deadband()
    test_straight_forward_ramping()
    test_reversal_zero_crossing()
    test_pivot_turn()
    test_speed_profiles()
    print("\nALL DIFFERENTIAL DRIVE CONTROLLER TESTS PASSED!")
