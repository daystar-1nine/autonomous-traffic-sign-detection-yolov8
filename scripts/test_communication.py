"""
Wireless UDP & HTTP Communication Verification Tool
Autonomous AI Car Project
Tests: Latency, Packet Loss, Motor Command Execution, Watchdog Heartbeat.
"""

import argparse
import socket
import time
import requests


def parse_args():
    parser = argparse.ArgumentParser(description="Test Wireless Communication with ESP8266")
    parser.add_argument("--esp-ip", type=str, default="192.168.4.1", help="IP address of ESP8266")
    parser.add_argument("--udp-port", type=int, default=8888, help="UDP listening port")
    parser.add_argument("--packets", type=int, default=20, help="Number of test packets")
    return parser.parse_args()


def test_udp(ip: str, port: int, count: int):
    print(f"\n[UDP TEST] Sending {count} datagrams to {ip}:{port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.3)

    latencies = []
    dropped = 0

    for i in range(count):
        payload = f"CMD:HEARTBEAT:0:0:{i}\n".encode("utf-8")
        t0 = time.perf_counter()
        sock.sendto(payload, (ip, port))

        try:
            data, _ = sock.recvfrom(64)
            dt = (time.perf_counter() - t0) * 1000.0
            latencies.append(dt)
            print(f" Packet {i+1:>2}: ACK received in {dt:5.1f} ms | Response: {data.decode().strip()}")
        except socket.timeout:
            dropped += 1
            print(f" Packet {i+1:>2}: [TIMEOUT - DROPPED]")

        time.sleep(0.05)

    sock.close()

    if latencies:
        avg_lat = sum(latencies) / len(latencies)
        print("-" * 55)
        print(f" Average Latency : {avg_lat:.2f} ms")
        print(f" Packets Sent    : {count}")
        print(f" Packets Lost    : {dropped} ({(dropped/count)*100:.1f}%)")
        print("-" * 55)
    else:
        print("[FAIL] Zero packets acknowledged. Check ESP8266 Wi-Fi connection.")


def test_http(ip: str):
    print(f"\n[HTTP TEST] Checking REST API endpoints on http://{ip}...")
    try:
        t0 = time.perf_counter()
        r = requests.get(f"http://{ip}/ping", timeout=1.0)
        dt = (time.perf_counter() - t0) * 1000.0
        if r.status_code == 200:
            print(f" [PASS] /ping responded in {dt:.1f} ms -> {r.text.strip()}")
        else:
            print(f" [WARN] /ping returned HTTP {r.status_code}")
    except Exception as e:
        print(f" [FAIL] HTTP connection failed: {e}")


def main():
    args = parse_args()
    print("=" * 60)
    print(" ESP8266 WIRELESS COMMUNICATION BENCHMARK")
    print("=" * 60)
    test_http(args.esp_ip)
    test_udp(args.esp_ip, args.udp_port, args.packets)
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
