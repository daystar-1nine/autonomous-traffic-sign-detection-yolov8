"""
Integration Test: Decision Engine State Machine & Safety Logic
06_TESTING/integration_tests/test_decision_engine.py
"""

import time


class MockDecisionEngine:
    def __init__(self):
        self.state = "CRUISING"
        self.consecutive_frames = 0
        self.last_sign = None
        self.cooldown_until = 0.0

    def update(self, detected_sign, h_ratio, manual=False):
        now = time.time()
        if manual:
            return "STOP", "MANUAL"

        if detected_sign == self.last_sign:
            self.consecutive_frames += 1
        else:
            self.consecutive_frames = 1
            self.last_sign = detected_sign

        is_confirmed = self.consecutive_frames >= 2
        in_cooldown = now < self.cooldown_until

        if is_confirmed and not in_cooldown:
            if detected_sign == "stop" and h_ratio >= 0.11:
                self.state = "STOPPED"
                return "STOP", "STOPPED"
            elif detected_sign == "left_turn" and h_ratio >= 0.11:
                self.state = "TURNING"
                self.cooldown_until = now + 2.5
                return "LEFT", "TURNING"

        return "FORWARD", "CRUISING"


def test_decision_logic():
    engine = MockDecisionEngine()

    # 1. Single frame blip should NOT trigger a stop (Debounce test)
    cmd, st = engine.update("stop", 0.15)
    assert cmd == "FORWARD", f"Expected FORWARD on single frame blip, got {cmd}"
    print(" [PASS] Single frame blip rejected by debounce filter.")

    # 2. Second consecutive frame confirms stop sign
    cmd, st = engine.update("stop", 0.15)
    assert cmd == "STOP", f"Expected STOP on confirmed detection, got {cmd}"
    assert st == "STOPPED"
    print(" [PASS] Two consecutive frames confirmed STOP maneuver.")

    # 3. Manual override overrides all autonomous commands
    cmd, st = engine.update("left_turn", 0.15, manual=True)
    assert cmd == "STOP"
    print(" [PASS] Manual override successfully forced STOP command.")

    print("\nALL DECISION ENGINE TESTS PASSED!")


if __name__ == "__main__":
    test_decision_logic()
