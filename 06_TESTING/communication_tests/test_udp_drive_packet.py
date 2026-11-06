"""
Unit Test: Dual-Protocol UDP Datagram Serialization & Deserialization
06_TESTING/communication_tests/test_udp_drive_packet.py
"""

def parse_udp_packet(payload: str):
    msg = payload.strip()
    if not msg.startswith("CMD:"):
        return None

    # 1. Direct Drive Format: "CMD:DRIVE:<LEFT>:<RIGHT>:<SEQ>"
    if msg.startswith("CMD:DRIVE:"):
        parts = msg.split(":")
        if len(parts) < 3:
            return None
        left = int(parts[2])
        right = int(parts[3]) if len(parts) > 3 else 0
        seq = int(parts[4]) if len(parts) > 4 else 0
        return {
            "type": "DRIVE",
            "left_pwm": max(-1023, min(1023, left)),
            "right_pwm": max(-1023, min(1023, right)),
            "seq": seq
        }

    # 2. Action Format: "CMD:<ACTION>:<SPEED>:<TRIM>:<SEQ>"
    parts = msg.split(":")
    action = parts[1]
    speed = int(parts[2]) if len(parts) > 2 else 700
    trim = int(parts[3]) if len(parts) > 3 else 0
    seq = int(parts[4]) if len(parts) > 4 else 0
    return {
        "type": "ACTION",
        "action": action,
        "speed": max(0, min(1023, speed)),
        "trim": max(-100, min(100, trim)),
        "seq": seq
    }


def test_drive_packet():
    # Direct drive forward packet
    fwd_pkt = "CMD:DRIVE:750:750:101\n"
    res = parse_udp_packet(fwd_pkt)
    assert res is not None
    assert res["type"] == "DRIVE"
    assert res["left_pwm"] == 750
    assert res["right_pwm"] == 750
    assert res["seq"] == 101
    print(" [PASS] Forward drive packet parsed accurately.")

    # Pivot turn packet (left forward, right reverse)
    turn_pkt = "CMD:DRIVE:600:-600:102\n"
    res = parse_udp_packet(turn_pkt)
    assert res["left_pwm"] == 600
    assert res["right_pwm"] == -600
    print(" [PASS] Bidirectional differential drive packet parsed accurately.")

    # Extreme value clamping
    overflow_pkt = "CMD:DRIVE:2500:-3000:103\n"
    res = parse_udp_packet(overflow_pkt)
    assert res["left_pwm"] == 1023
    assert res["right_pwm"] == -1023
    print(" [PASS] Hardware PWM boundary clamping enforced [-1023, +1023].")


def test_backward_compatibility_action_packet():
    action_pkt = "CMD:FORWARD:700:0:55\n"
    res = parse_udp_packet(action_pkt)
    assert res is not None
    assert res["type"] == "ACTION"
    assert res["action"] == "FORWARD"
    assert res["speed"] == 700
    assert res["seq"] == 55
    print(" [PASS] Backward compatibility with Autonomous Action packets verified.")


if __name__ == "__main__":
    test_drive_packet()
    test_backward_compatibility_action_packet()
    print("\nALL UDP DUAL-PROTOCOL PACKET TESTS PASSED!")
