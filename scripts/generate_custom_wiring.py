#!/usr/bin/env python3
"""
Custom Hardware Wiring Diagram for User's Exact Physical Pins:
- Motor A (Left) : AIN1 = D1, AIN2 = D2, PWMA = D5
- Motor B (Right): BIN1 = D7, BIN2 = D4, PWMB = D6
- Standby        : STBY = D0
- LM2596 Buck Converter + Mini Breadboard + 2S Li-ion Battery
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

def generate_exact_user_wiring_diagram(output_paths):
    fig, ax = plt.subplots(figsize=(24, 15), dpi=300)
    fig.patch.set_facecolor('#0B0F19')
    ax.set_facecolor('#0B0F19')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Title Banner
    ax.text(50, 96.5, "YOUR EXACT HARDWARE WIRING DIAGRAM (MATCHING YOUR CODE)", 
            fontsize=24, fontweight='bold', color='#38BDF8', ha='center', va='center')
    ax.text(50, 93.8, "Motor A (Left): D1, D2, D5 | Motor B (Right): D7, D4, D6 | Standby: D0 | Zero Rewiring Needed!",
            fontsize=13, color='#4ADE80', fontweight='bold', ha='center', va='center')

    def draw_comp(x, y, w, h, bg, border, title, sub=""):
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=1.2",
                              facecolor=bg, edgecolor=border, linewidth=2.5, zorder=2)
        ax.add_patch(rect)
        if title:
            ax.text(x + w/2, y + h - 2.2, title, fontsize=13, fontweight='bold', color='#FFFFFF', ha='center', va='center', zorder=3)
        if sub:
            ax.text(x + w/2, y + h - 4.5, sub, fontsize=10, color='#94A3B8', ha='center', va='center', zorder=3)

    def draw_pin(x, y, label, col='#38BDF8', is_left=True):
        ax.add_patch(plt.Circle((x, y), 0.65, color=col, zorder=5))
        offset = 1.1 if is_left else -1.1
        align = 'left' if is_left else 'right'
        ax.text(x + offset, y, label, fontsize=10, fontweight='bold', color='#F1F5F9', ha=align, va='center', zorder=5)

    def draw_wire(pts, col, width=2.5):
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=col, linewidth=width, zorder=3, alpha=0.95)

    # 1. 2S 18650 Battery Holder (Top Left)
    draw_comp(5, 71, 20, 18, '#1E293B', '#A855F7', "2x 18650 Battery Holder", "7.4V Nom / 8.4V (2x Purple Cells)")
    c1 = FancyBboxPatch((7, 73.5), 7, 10, boxstyle="round,pad=0.1,rounding_size=0.5", facecolor='#7E22CE', edgecolor='#C084FC', linewidth=1.5, zorder=3)
    c2 = FancyBboxPatch((16, 73.5), 7, 10, boxstyle="round,pad=0.1,rounding_size=0.5", facecolor='#7E22CE', edgecolor='#C084FC', linewidth=1.5, zorder=3)
    ax.add_patch(c1); ax.add_patch(c2)
    ax.text(10.5, 78.5, "18650\nPurple", color='#F3E8FF', fontsize=10, fontweight='bold', ha='center', va='center', zorder=4)
    ax.text(19.5, 78.5, "18650\nPurple", color='#F3E8FF', fontsize=10, fontweight='bold', ha='center', va='center', zorder=4)
    bat_red = (25, 83); bat_blk = (25, 74)
    draw_pin(bat_red[0], bat_red[1], "Red (+)", '#EF4444', is_left=False)
    draw_pin(bat_blk[0], bat_blk[1], "Black (-)", '#64748B', is_left=False)

    # 2. LM2596 Buck Converter (Top Middle)
    draw_comp(33, 71, 20, 18, '#1E293B', '#2563EB', "LM2596S Buck Converter", "Blue Board with Brass Potentiometer")
    pot = FancyBboxPatch((40, 74), 6, 6, boxstyle="round,pad=0.1,rounding_size=0.3", facecolor='#1D4ED8', edgecolor='#60A5FA', zorder=3)
    ax.add_patch(pot)
    ax.add_patch(plt.Circle((43, 77), 1.2, color='#FCD34D', zorder=4))
    ax.text(43, 81.5, "W103 Pot (Set 5.15V)", color='#93C5FD', fontsize=8.5, ha='center', va='center', zorder=4)
    b_inp = (33, 83); b_inm = (33, 74)
    b_outp = (53, 83); b_outm = (53, 74)
    draw_pin(b_inp[0], b_inp[1], "IN+ (Red)", '#EF4444', is_left=True)
    draw_pin(b_inm[0], b_inm[1], "IN- (Black)", '#64748B', is_left=True)
    draw_pin(b_outp[0], b_outp[1], "OUT+ (White)", '#FFFFFF', is_left=False)
    draw_pin(b_outm[0], b_outm[1], "OUT- (Purple)", '#A855F7', is_left=False)

    # 3. Mini Breadboard Strip (Center Top-Right)
    draw_comp(62, 70, 12, 20, '#F8FAFC', '#94A3B8', "Mini Breadboard", "Power Hub Bus")
    ax.add_patch(patches.Rectangle((64, 72), 3, 15, facecolor='#FEE2E2', edgecolor='#EF4444', linewidth=1.5, zorder=3))
    ax.add_patch(patches.Rectangle((69, 72), 3, 15, facecolor='#E0F2FE', edgecolor='#0284C7', linewidth=1.5, zorder=3))
    ax.text(65.5, 85, "+5.15V", color='#DC2626', fontsize=8, fontweight='bold', ha='center', va='center', zorder=4)
    ax.text(70.5, 85, "GND", color='#0369A1', fontsize=8, fontweight='bold', ha='center', va='center', zorder=4)
    bb_v_in = (64, 83); bb_g_in = (69, 74)

    # 4. NodeMCU ESP-12E (Right Center)
    draw_comp(79, 30, 18, 60, '#1E293B', '#0284C7', "NodeMCU ESP-12E", "Your Exact Working Pins")
    ax.add_patch(FancyBboxPatch((83, 68), 10, 11, boxstyle="round,pad=0.1,rounding_size=0.4", facecolor='#334155', edgecolor='#94A3B8', zorder=3))
    ax.text(88, 73.5, "ESP-12E\nWiFi", color='#FFFFFF', fontsize=9, fontweight='bold', ha='center', va='center', zorder=4)

    # NodeMCU Left Header Pins (Exact to your code)
    nm_left = {
        "D0 (STBY)": (79, 65, '#C084FC'),  # STBY
        "D1 (AIN1)": (79, 60, '#4ADE80'),  # AIN1
        "D2 (AIN2)": (79, 55, '#FACC15'),  # AIN2
        "D4 (BIN2)": (79, 50, '#E879F9'),  # BIN2
        "D5 (PWMA)": (79, 45, '#38BDF8'),  # PWMA
        "D6 (PWMB)": (79, 40, '#818CF8'),  # PWMB
        "D7 (BIN1)": (79, 35, '#2DD4BF'),  # BIN1
    }
    for lbl, (px, py, c) in nm_left.items():
        draw_pin(px, py, lbl, c, is_left=True)

    nm_right = {
        "VIN (5.15V)": (97, 85, '#EF4444'),
        "GND":         (97, 80, '#64748B'),
        "3V3 (VCC)":   (97, 65, '#FB923C'),
    }
    for lbl, (px, py, c) in nm_right.items():
        draw_pin(px, py, lbl, c, is_left=False)

    # 5. TB6612FNG HW-166 (Red Board, Bottom Center)
    draw_comp(32, 10, 34, 52, '#1E293B', '#DC2626', "TB6612FNG (HW-166)", "Red Motor Driver Board (16 Pins)")
    ax.add_patch(FancyBboxPatch((44, 29), 10, 14, boxstyle="round,pad=0.1,rounding_size=0.3", facecolor='#0F172A', edgecolor='#EF4444', zorder=3))
    ax.text(49, 36, "TB6612\nHW-166", color='#FCA5A5', fontsize=10, fontweight='bold', ha='center', va='center', zorder=4)

    # TB6612 Left (Control)
    tb_l = {
        "PWMA (D5)": (32, 55, '#38BDF8'),
        "AIN2 (D2)": (32, 49, '#FACC15'),
        "AIN1 (D1)": (32, 43, '#4ADE80'),
        "STBY (D0)": (32, 37, '#C084FC'),
        "BIN1 (D7)": (32, 31, '#2DD4BF'),
        "BIN2 (D4)": (32, 25, '#E879F9'),
        "PWMB (D6)": (32, 19, '#818CF8'),
        "GND":       (32, 13, '#64748B')
    }
    for lbl, (px, py, c) in tb_l.items():
        draw_pin(px, py, lbl, c, is_left=True)

    # TB6612 Right (Power & Motor Out)
    tb_r = {
        "VM (Battery 7.4V)": (66, 55, '#EF4444'),
        "VCC (3.3V Logic)":  (66, 49, '#FB923C'),
        "GND":               (66, 43, '#64748B'),
        "AO1 (Left Mtr +)":  (66, 37, '#FCD34D'),
        "AO2 (Left Mtr -)":  (66, 31, '#FCD34D'),
        "BO2 (Right Mtr -)": (66, 25, '#38BDF8'),
        "BO1 (Right Mtr +)": (66, 19, '#38BDF8'),
        "GND":               (66, 13, '#64748B')
    }
    for lbl, (px, py, c) in tb_r.items():
        draw_pin(px, py, lbl, c, is_left=False)

    # 6. Motors
    # Left Motor
    draw_comp(4, 25, 20, 18, '#1E293B', '#F59E0B', "Left TT DC Motor", "Motor A (AO1 / AO2)")
    ax.add_patch(FancyBboxPatch((6, 27), 7, 10, boxstyle="round,pad=0.1,rounding_size=0.4", facecolor='#D97706', edgecolor='#FBBF24', zorder=3))
    ax.add_patch(FancyBboxPatch((15, 26), 6, 12, boxstyle="round,pad=0.1,rounding_size=0.8", facecolor='#111827', edgecolor='#4B5563', linewidth=2, zorder=3))
    ax.text(9.5, 32, "Yellow\nMotor", color='#FEF3C7', fontsize=9, fontweight='bold', ha='center', va='center', zorder=4)
    ax.text(18, 32, "Wheel", color='#9CA3AF', fontsize=9, ha='center', va='center', zorder=4)
    ml1 = (24, 37); ml2 = (24, 31)
    draw_pin(ml1[0], ml1[1], "Wire 1", '#FCD34D', is_left=False)
    draw_pin(ml2[0], ml2[1], "Wire 2", '#FCD34D', is_left=False)

    # Right Motor
    draw_comp(75, 5, 21, 18, '#1E293B', '#38BDF8', "Right TT DC Motor", "Motor B (BO1 / BO2)")
    ax.add_patch(FancyBboxPatch((77, 7), 7, 10, boxstyle="round,pad=0.1,rounding_size=0.4", facecolor='#0284C7', edgecolor='#38BDF8', zorder=3))
    ax.add_patch(FancyBboxPatch((86, 6), 6, 12, boxstyle="round,pad=0.1,rounding_size=0.8", facecolor='#111827', edgecolor='#4B5563', linewidth=2, zorder=3))
    ax.text(80.5, 12, "Yellow\nMotor", color='#E0F2FE', fontsize=9, fontweight='bold', ha='center', va='center', zorder=4)
    ax.text(89, 12, "Wheel", color='#9CA3AF', fontsize=9, ha='center', va='center', zorder=4)
    mr1 = (75, 17); mr2 = (75, 11)
    draw_pin(mr1[0], mr1[1], "Wire 1", '#38BDF8', is_left=True)
    draw_pin(mr2[0], mr2[1], "Wire 2", '#38BDF8', is_left=True)

    # ==================== EXACT WIRING CONNECTIONS ====================
    # 1. Battery to Buck IN
    draw_wire([bat_red, (29, 83), b_inp], '#EF4444', width=3)
    draw_wire([bat_blk, (29, 74), b_inm], '#64748B', width=3)

    # 2. Buck OUT to Mini Breadboard
    draw_wire([b_outp, (58, 83), bb_v_in], '#F8FAFC', width=3) # White wire
    draw_wire([b_outm, (58, 74), bb_g_in], '#A855F7', width=3) # Purple wire

    # 3. High Voltage Motor Power (VM)
    draw_wire([(29, 83), (29, 88), (71, 88), (71, 55), (66, 55)], '#EF4444', width=3)

    # 4. Breadboard Power to NodeMCU
    draw_wire([(65.5, 76), (65.5, 91), (99, 91), (99, 85), (97, 85)], '#EF4444', width=3)
    draw_wire([(70.5, 76), (70.5, 87), (98, 87), (98, 80), (97, 80)], '#64748B', width=2.5)

    # 5. Breadboard Ground to TB6612 GND
    draw_wire([(70.5, 72), (70.5, 60), (30, 60), (30, 13), (32, 13)], '#64748B', width=2.5)
    draw_wire([(66, 43), (68, 43), (68, 60)], '#64748B', width=2.0)

    # 6. NodeMCU 3V3 to TB6612 VCC
    draw_wire([(97, 65), (100, 65), (100, 49), (66, 49)], '#FB923C', width=2.5)

    # 7. Motor Driver Control Wires (NodeMCU to TB6612 Left) - EXACT MATCH
    # D5 -> PWMA
    draw_wire([(79, 45), (74, 45), (74, 55), (32, 55)], '#38BDF8', width=2)
    # D2 -> AIN2
    draw_wire([(79, 55), (73, 55), (73, 49), (32, 49)], '#FACC15', width=2)
    # D1 -> AIN1
    draw_wire([(79, 60), (72, 60), (72, 43), (32, 43)], '#4ADE80', width=2)
    # D0 -> STBY
    draw_wire([(79, 65), (71, 65), (71, 37), (32, 37)], '#C084FC', width=2)
    # D7 -> BIN1
    draw_wire([(79, 35), (70, 35), (70, 31), (32, 31)], '#2DD4BF', width=2)
    # D4 -> BIN2
    draw_wire([(79, 50), (69, 50), (69, 25), (32, 25)], '#E879F9', width=2)
    # D6 -> PWMB
    draw_wire([(79, 40), (68, 40), (68, 19), (32, 19)], '#818CF8', width=2)

    # 8. Motor Terminals
    draw_wire([(66, 37), (68, 37), (68, 40), (26, 40), ml1], '#FCD34D', width=2.5)
    draw_wire([(66, 31), (67, 31), (67, 34), (26, 34), ml2], '#F59E0B', width=2.5)
    draw_wire([(66, 19), (71, 19), (71, 17), mr1], '#38BDF8', width=2.5)
    draw_wire([(66, 25), (70, 25), (70, 11), mr2], '#0284C7', width=2.5)

    # Notes Box
    draw_comp(5, 2, 90, 6, '#1E293B', '#10B981', "EXACT CODE-ALIGNED WIRING SUMMARY", "")
    ax.text(6, 4.2, "• Motor A (Left): AIN1 = D1, AIN2 = D2, PWMA = D5 | Motor B (Right): BIN1 = D7, BIN2 = D4, PWMB = D6 | STBY = D0", fontsize=10.5, color='#86EFAC', fontweight='bold', va='center')
    ax.text(6, 2.2, "• Wi-Fi Dual Mode: Automatically connects to hotspot 'Kunal@Bsnl' AND broadcasts direct AP 'AutonomousCar_AP'!", fontsize=10, color='#F8FAFC', va='center')

    plt.tight_layout()
    for p in output_paths:
        d = os.path.dirname(p)
        if d:
            os.makedirs(d, exist_ok=True)
        plt.savefig(p, format='png', bbox_inches='tight', dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
        print(f"[SUCCESS] Custom wiring diagram saved to: {p}")
    plt.close()

if __name__ == "__main__":
    artifact_dir = r"C:\Users\suraj\.gemini\antigravity\brain\2a3e79a3-7671-431d-92eb-1b2bc379821c"
    paths = [
        os.path.join("docs", "custom_hardware_wiring.png"),
        os.path.join(artifact_dir, "custom_hardware_wiring.png"),
        "custom_hardware_wiring.png"
    ]
    generate_exact_user_wiring_diagram(paths)
