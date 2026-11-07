"""
Integration Test: Decision Engine State Machine & Safety Logic
06_TESTING/integration_tests/test_decision_engine.py
"""

import time


class MockDecisionEngine:
    def __init__(self, turn_duration=0.65, cooldown=3.0):
        self.state = "CRUISING"
        self.consecutive_frames = 0
        self.last_sign = None
        self.turn_duration = turn_duration
        self.turn_start_time = 0.0
        self.cooldown_duration = cooldown
        self.cooldown_until = 0.0
        self.active_turn_cmd = "FORWARD"

    def update(self, detected_sign, h_ratio, manual=False, custom_time=None):
        now = time.time() if custom_time is None else custom_time
        if manual:
            return "STOP", "MANUAL"

        if detected_sign == self.last_sign:
            self.consecutive_frames += 1
        else:
            self.consecutive_frames = 1
            self.last_sign = detected_sign

        is_confirmed = self.consecutive_frames >= 2

        # 1. Stop / Hazard priority
        if is_confirmed and detected_sign == "stop" and h_ratio >= 0.05:
            self.state = "STOPPED"
            return "STOP", "STOPPED"

        # 2. In-progress turn
        if self.state == "TURNING":
            if now - self.turn_start_time < self.turn_duration:
                return self.active_turn_cmd, "TURNING"
            else:
                self.state = "POST_TURN_CRUISE"

        # 3. Turn sign processing with cooldown refractory check
        if is_confirmed and detected_sign in ["left_turn", "right_turn"] and h_ratio >= 0.05:
            if now < self.cooldown_until:
                # In cooldown: car has turned and is cruising straight past sign!
                return "FORWARD", "CRUISING"
            else:
                self.state = "TURNING"
                self.turn_start_time = now
                self.active_turn_cmd = "LEFT" if detected_sign == "left_turn" else "RIGHT"
                self.cooldown_until = now + self.cooldown_duration
                return self.active_turn_cmd, "TURNING"

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

    # 4. Turn-and-Cruise: Sign triggers turn for 650ms, then straight cruise without endless spinning
    t0 = 1000.0
    # Frame 1 of right turn
    cmd, st = engine.update("right_turn", 0.10, custom_time=t0)
    # Frame 2: Confirmed right turn begins
    cmd, st = engine.update("right_turn", 0.10, custom_time=t0 + 0.033)
    assert cmd == "RIGHT" and st == "TURNING", f"Expected RIGHT/TURNING, got {cmd}/{st}"
    print(" [PASS] Turn sign confirmed -> Executing RIGHT turn arc.")

    # At 700ms (after 650ms turn arc finished), even if camera STILL sees right_turn:
    # Must cruise FORWARD and NOT spin again!
    cmd, st = engine.update("right_turn", 0.10, custom_time=t0 + 0.70)
    assert cmd == "FORWARD", f"Expected FORWARD after turn completion, got {cmd}"
    print(" [PASS] Post-turn cruise engaged: Car cruises FORWARD and suppresses re-spinning.")

    print("\nALL DECISION ENGINE TESTS PASSED!")


if __name__ == "__main__":
    test_decision_logic()
