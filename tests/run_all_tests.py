#!/usr/bin/env python3
"""
Master Test Runner
Runs all unit, integration, protocol, and model tests across the test suite.
"""

import subprocess
import sys
import os
import time

TEST_FILES = [
    "tests/controller_tests/test_differential_drive.py",
    "tests/controller_tests/test_mode_manager.py",
    "tests/communication_tests/test_udp_drive_packet.py",
    "tests/communication_tests/test_udp_mock.py",
    "tests/integration_tests/test_decision_engine.py",
    "tests/model_tests/test_model_inference.py"
]

def main():
    print("=================================================================")
    print("  AUTONOMOUS CAR DUAL-MODE TEST HARNESS - COMPLETE VERIFICATION  ")
    print("=================================================================")
    total_passed = 0
    total_failed = 0
    start_time = time.time()

    for test_file in TEST_FILES:
        if not os.path.exists(test_file):
            print(f"[SKIP] {test_file} not found.")
            continue

        print(f"\n--- Running: {test_file} ---")
        res = subprocess.run([sys.executable, test_file], capture_output=True, text=True)
        if res.returncode == 0:
            print(res.stdout.strip())
            print(f"[PASS] {test_file}")
            total_passed += 1
        else:
            print(res.stdout.strip())
            print(res.stderr.strip())
            print(f"[FAIL] {test_file}")
            total_failed += 1

    elapsed = time.time() - start_time
    print("\n=================================================================")
    print(f"TEST RUN SUMMARY: {total_passed} Passed, {total_failed} Failed in {elapsed:.2f}s")
    print("=================================================================")
    
    if total_failed == 0:
        print("[SUCCESS] ALL TESTS COMPLETED WITH 100% PASS RATE!")
        sys.exit(0)
    else:
        print("[FAILURE] Some tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
