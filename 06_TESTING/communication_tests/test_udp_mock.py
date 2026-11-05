"""
Unit Test: UDP Command Protocol Serialization & Parsing
06_TESTING/communication_tests/test_udp_mock.py
"""

def parse_udp_command(payload: str):
    if not payload.startswith("CMD:"):
        return None
    parts = payload.strip().split(":")
    if len(parts) < 2:
        return None
    action = parts[1]
    speed = int(parts[2]) if len(parts) > 2 else 700
    trim = int(parts[3]) if len(parts) > 3 else 0
    seq = int(parts[4]) if len(parts) > 4 else 0
    return {"action": action, "speed": speed, "trim": trim, "seq": seq}


def test_udp_protocol():
    packet = "CMD:FORWARD:700:5:102\n"
    res = parse_udp_command(packet)
    assert res is not None, "Failed to parse valid packet"
    assert res["action"] == "FORWARD"
    assert res["speed"] == 700
    assert res["trim"] == 5
    assert res["seq"] == 102
    print(" [PASS] Valid packet parsed correctly.")

    invalid = "MALFORMED_PACKET"
    assert parse_udp_command(invalid) is None
    print(" [PASS] Malformed packet rejected.")

    print("\nALL UDP PROTOCOL TESTS PASSED!")


if __name__ == "__main__":
    test_udp_protocol()
