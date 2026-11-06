#!/usr/bin/env python3
"""
Hardware Wiring Diagram Generator
Autonomous AI Traffic Sign Detection Car
Generates a professional, high-resolution, color-coded schematic diagram
for NodeMCU ESP8266 + TB6612FNG + LM2596 Buck Converter + 2S Li-ion Battery + TT Motors.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Arrow

def create_wiring_diagram(output_paths):
    fig, ax = plt.subplots(figsize=(24, 15), dpi=300)
    fig.patch.set_facecolor('#0F172A') # Dark slate background
    ax.set_facecolor('#0F172A')

    # Canvas dimensions: 0 to 100 on X, 0 to 100 on Y
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # ==================== TITLE & BANNER ====================
    ax.text(50, 96.5, "AUTONOMOUS AI CAR — COMPLETE HARDWARE WIRING DIAGRAM", 
            fontsize=26, fontweight='bold', color='#38BDF8', ha='center', va='center', fontfamily='sans-serif')
    ax.text(50, 93.8, "NodeMCU ESP8266 (ESP-12E) + TB6612FNG Dual Driver + LM2596 Buck (5.15V) + 2S Li-ion Battery (7.4V-8.4V)",
            fontsize=15, color='#94A3B8', ha='center', va='center', fontfamily='sans-serif')

    # Helper function for rounded component boxes
    def draw_box(x, y, w, h, bg_color, border_color, title, subtitle="", corner_radius=1.5):
        rect = FancyBboxPatch((x, y), w, h,
                              boxstyle=f"round,pad=0.2,rounding_size={corner_radius}",
                              facecolor=bg_color, edgecolor=border_color, linewidth=2.5, zorder=2)
        ax.add_patch(rect)
        if title:
            ax.text(x + w/2, y + h - 2.2, title, fontsize=15, fontweight='bold', color='#F8FAFC', 
                    ha='center', va='center', zorder=3)
        if subtitle:
            ax.text(x + w/2, y + h - 4.5, subtitle, fontsize=11, color='#94A3B8', 
                    ha='center', va='center', zorder=3)

    # Helper for pin rows
    def draw_pin(x, y, label, color='#38BDF8', is_left=True, pin_color='#1E293B'):
        # Small circle pin header
        circle = plt.Circle((x, y), 0.7, color=color, zorder=4)
        ax.add_patch(circle)
        offset = 1.2 if is_left else -1.2
        align = 'left' if is_left else 'right'
        ax.text(x + offset, y, label, fontsize=11, fontweight='bold', color='#F1F5F9',
                ha=align, va='center', zorder=4)

    # ==================== 1. BATTERY PACK (TOP LEFT) ====================
    draw_box(4, 70, 18, 18, '#1E293B', '#10B981', "2S Li-ion Battery Pack", "7.4V Nom / 8.4V Peak (2S BMS)")
    # Draw two 18650 cell graphics
    cell1 = FancyBboxPatch((6, 73), 6, 9, boxstyle="round,pad=0.1,rounding_size=0.5", facecolor='#065F46', edgecolor='#34D399', linewidth=1.5, zorder=3)
    cell2 = FancyBboxPatch((14, 73), 6, 9, boxstyle="round,pad=0.1,rounding_size=0.5", facecolor='#065F46', edgecolor='#34D399', linewidth=1.5, zorder=3)
    ax.add_patch(cell1)
    ax.add_patch(cell2)
    ax.text(9, 77.5, "18650\n3.7V", color='#ECFDF5', fontsize=10, ha='center', va='center', fontweight='bold', zorder=4)
    ax.text(17, 77.5, "18650\n3.7V", color='#ECFDF5', fontsize=10, ha='center', va='center', fontweight='bold', zorder=4)

    # Battery output pins
    bat_plus = (22, 83)
    bat_minus = (22, 73)
    draw_pin(bat_plus[0], bat_plus[1], "BAT (+)", '#EF4444', is_left=False)
    draw_pin(bat_minus[0], bat_minus[1], "BAT (-)", '#64748B', is_left=False)

    # ==================== 2. SPST POWER SWITCH (TOP CENTER-LEFT) ====================
    draw_box(29, 78, 10, 10, '#1E293B', '#F59E0B', "SPST Switch", "Master Power")
    sw_in = (29, 83)
    sw_out = (39, 83)
    draw_pin(sw_in[0], sw_in[1], "IN", '#EF4444', is_left=True)
    draw_pin(sw_out[0], sw_out[1], "OUT", '#EF4444', is_left=False)

    # ==================== 3. LM2596 BUCK CONVERTER (TOP CENTER) ====================
    draw_box(45, 69, 20, 19, '#1E293B', '#3B82F6', "LM2596 Buck Converter", "Output Trimmed to 5.15V DC")
    # Draw potentiometer graphic
    pot = FancyBboxPatch((52, 72.5), 6, 6, boxstyle="round,pad=0.1,rounding_size=0.3", facecolor='#1D4ED8', edgecolor='#60A5FA', linewidth=1.5, zorder=3)
    ax.add_patch(pot)
    pot_screw = plt.Circle((55, 75.5), 1.2, color='#FCD34D', zorder=4)
    ax.add_patch(pot_screw)
    ax.text(55, 75.5, "+", color='#78350F', fontsize=12, fontweight='bold', ha='center', va='center', zorder=5)
    ax.text(55, 80.5, "Trim Pot: 5.15V", color='#93C5FD', fontsize=9, ha='center', va='center', zorder=4)

    # Buck pins
    buck_in_plus = (45, 83)
    buck_in_minus = (45, 73)
    buck_out_plus = (65, 83)
    buck_out_minus = (65, 73)
    draw_pin(buck_in_plus[0], buck_in_plus[1], "IN+", '#EF4444', is_left=True)
    draw_pin(buck_in_minus[0], buck_in_minus[1], "IN-", '#64748B', is_left=True)
    draw_pin(buck_out_plus[0], buck_out_plus[1], "OUT+ (5.15V)", '#EF4444', is_left=False)
    draw_pin(buck_out_minus[0], buck_out_minus[1], "OUT- (GND)", '#64748B', is_left=False)

    # ==================== 4. NODEMCU ESP8266 (CENTER RIGHT) ====================
    draw_box(73, 40, 23, 48, '#1E293B', '#0284C7', "NodeMCU ESP8266", "ESP-12E WiFi Brain (Zero AI)")
    # Draw chip graphic
    esp_chip = FancyBboxPatch((78, 68), 13, 13, boxstyle="round,pad=0.1,rounding_size=0.5", facecolor='#334155', edgecolor='#94A3B8', linewidth=1.5, zorder=3)
    ax.add_patch(esp_chip)
    ax.text(84.5, 75.5, "ESP8266\nESP-12E", color='#F8FAFC', fontsize=11, fontweight='bold', ha='center', va='center', zorder=4)
    # Antenna trace
    ant = FancyBboxPatch((80, 81), 9, 3, boxstyle="round,pad=0.05,rounding_size=0.2", facecolor='#B45309', edgecolor='#FBBF24', zorder=3)
    ax.add_patch(ant)

    # NodeMCU Left Header Pins (used for motor control)
    node_pins = {
        "D1 (GPIO 5)": (73, 62, '#38BDF8'),   # Left PWM
        "D2 (GPIO 4)": (73, 58, '#4ADE80'),   # Left AIN1
        "D3 (GPIO 0)": (73, 54, '#FACC15'),   # Left AIN2
        "D5 (GPIO 14)": (73, 50, '#2DD4BF'),  # Right BIN1
        "D6 (GPIO 12)": (73, 46, '#E879F9'),  # Right BIN2
        "D7 (GPIO 13)": (73, 42, '#818CF8'),  # Right PWMB
    }
    for label, (px, py, col) in node_pins.items():
        draw_pin(px, py, label, col, is_left=True)

    # NodeMCU Right Header Pins
    node_right_pins = {
        "D8 (GPIO 15)": (96, 62, '#C084FC'),  # STBY
        "3V3 Logic Out": (96, 54, '#FB923C'), # 3.3V out to TB6612 VCC
        "GND (Common)": (96, 48, '#64748B'),  # GND
        "VIN (5.15V In)": (96, 42, '#EF4444') # 5.15V power input
    }
    for label, (px, py, col) in node_right_pins.items():
        draw_pin(px, py, label, col, is_left=False)

    # ==================== 5. TB6612FNG MOTOR DRIVER (BOTTOM CENTER) ====================
    draw_box(33, 14, 30, 48, '#1E293B', '#EC4899', "TB6612FNG Dual Motor Driver", "High Efficiency MOSFET H-Bridge (Peak 3.2A)")
    
    # TB6612 IC Graphic in center
    tb_ic = FancyBboxPatch((43, 30), 10, 16, boxstyle="round,pad=0.1,rounding_size=0.3", facecolor='#0F172A', edgecolor='#F43F5E', linewidth=1.5, zorder=3)
    ax.add_patch(tb_ic)
    ax.text(48, 38, "TB6612\nFNG", color='#FDA4AF', fontsize=11, fontweight='bold', ha='center', va='center', zorder=4)

    # TB6612 Left Pins (Logic Control Inputs)
    tb_logic_pins = {
        "PWMA (Left Speed)": (33, 56, '#38BDF8'),
        "AIN1 (Left Dir 1)": (33, 51, '#4ADE80'),
        "AIN2 (Left Dir 2)": (33, 46, '#FACC15'),
        "STBY (Standby)":    (33, 41, '#C084FC'),
        "BIN1 (Right Dir 1)":(33, 36, '#2DD4BF'),
        "BIN2 (Right Dir 2)":(33, 31, '#E879F9'),
        "PWMB (Right Speed)":(33, 26, '#818CF8'),
        "GND (Logic Ground)":(33, 19, '#64748B')
    }
    for label, (px, py, col) in tb_logic_pins.items():
        draw_pin(px, py, label, col, is_left=True)

    # TB6612 Right Pins (Power & Motor Outputs)
    tb_power_pins = {
        "VM (7.4V Motor Power)": (63, 56, '#EF4444'),
        "VCC (3.3V Logic In)":   (63, 50, '#FB923C'),
        "GND (Power Ground)":    (63, 44, '#64748B'),
        "AO1 (Left Motor +)":    (63, 38, '#FCD34D'),
        "AO2 (Left Motor -)":    (63, 33, '#FCD34D'),
        "BO1 (Right Motor +)":   (63, 27, '#38BDF8'),
        "BO2 (Right Motor -)":   (63, 21, '#38BDF8')
    }
    for label, (px, py, col) in tb_power_pins.items():
        draw_pin(px, py, label, col, is_left=False)

    # ==================== 6. LEFT & RIGHT TT DC MOTORS ====================
    # Left Motor (Bottom Left)
    draw_box(4, 25, 20, 18, '#1E293B', '#F59E0B', "Left TT DC Motor", "1:48 Geared (AO1 / AO2)")
    # Gearbox and wheel graphic
    gear1 = FancyBboxPatch((6, 27), 7, 10, boxstyle="round,pad=0.1,rounding_size=0.4", facecolor='#D97706', edgecolor='#FBBF24', zorder=3)
    wheel1 = FancyBboxPatch((15, 26), 6, 12, boxstyle="round,pad=0.1,rounding_size=0.8", facecolor='#111827', edgecolor='#4B5563', linewidth=2, zorder=3)
    ax.add_patch(gear1)
    ax.add_patch(wheel1)
    ax.text(9.5, 32, "Left\nGear", color='#FEF3C7', fontsize=9, fontweight='bold', ha='center', va='center', zorder=4)
    ax.text(18, 32, "Wheel", color='#9CA3AF', fontsize=9, ha='center', va='center', zorder=4)
    motor_left_p1 = (24, 38)
    motor_left_p2 = (24, 33)
    draw_pin(motor_left_p1[0], motor_left_p1[1], "Term 1", '#FCD34D', is_left=False)
    draw_pin(motor_left_p2[0], motor_left_p2[1], "Term 2", '#FCD34D', is_left=False)

    # Right Motor (Bottom Right)
    draw_box(73, 10, 23, 18, '#1E293B', '#38BDF8', "Right TT DC Motor", "1:48 Geared (BO1 / BO2)")
    gear2 = FancyBboxPatch((75, 12), 7, 10, boxstyle="round,pad=0.1,rounding_size=0.4", facecolor='#0284C7', edgecolor='#38BDF8', zorder=3)
    wheel2 = FancyBboxPatch((84, 11), 6, 12, boxstyle="round,pad=0.1,rounding_size=0.8", facecolor='#111827', edgecolor='#4B5563', linewidth=2, zorder=3)
    ax.add_patch(gear2)
    ax.add_patch(wheel2)
    ax.text(78.5, 17, "Right\nGear", color='#E0F2FE', fontsize=9, fontweight='bold', ha='center', va='center', zorder=4)
    ax.text(87, 17, "Wheel", color='#9CA3AF', fontsize=9, ha='center', va='center', zorder=4)
    motor_right_p1 = (73, 22)
    motor_right_p2 = (73, 17)
    draw_pin(motor_right_p1[0], motor_right_p1[1], "Term 1", '#38BDF8', is_left=True)
    draw_pin(motor_right_p2[0], motor_right_p2[1], "Term 2", '#38BDF8', is_left=True)

    # ==================== WIRING CONNECTIONS (COLOR-CODED TRACES) ====================
    def draw_wire(points, color, width=2.5, style='-', alpha=0.9):
        xs, ys = zip(*points)
        ax.plot(xs, ys, color=color, linewidth=width, linestyle=style, alpha=alpha, zorder=2)

    # 1. Battery (+) -> Switch IN
    draw_wire([bat_plus, (25.5, 83), sw_in], '#EF4444')

    # 2. Switch OUT -> Split into: (a) Buck IN+, (b) TB6612 VM
    sw_junction = (42, 83)
    draw_wire([sw_out, sw_junction], '#EF4444')
    draw_wire([sw_junction, buck_in_plus], '#EF4444') # To Buck IN+
    # High-Voltage line to TB6612 VM (curves down right side)
    draw_wire([sw_junction, (42, 86.5), (68, 86.5), (68, 56), tb_power_pins["VM (7.4V Motor Power)"][:2]], '#EF4444', width=3.0)

    # 3. COMMON STAR GROUND (Black Wires)
    gnd_star = (27, 65)
    # Battery (-) to Star GND
    draw_wire([bat_minus, (24, 73), (24, 65), gnd_star], '#64748B', width=3.0)
    # Buck IN- to Star GND
    draw_wire([buck_in_minus, (38, 73), (38, 65), gnd_star], '#64748B', width=2.5)
    # Buck OUT- to Star GND
    draw_wire([buck_out_minus, (66.5, 73), (66.5, 65), gnd_star], '#64748B', width=2.5)
    # Star GND to TB6612 GND
    draw_wire([gnd_star, (27, 44), (30, 44), (30, 19), tb_logic_pins["GND (Logic Ground)"][:2]], '#64748B', width=2.5)
    draw_wire([(30, 44), (64.5, 44), tb_power_pins["GND (Power Ground)"][:2]], '#64748B', width=2.0)
    # Star GND to NodeMCU GND
    draw_wire([gnd_star, (27, 67), (70, 67), (70, 48), (96, 48)], '#64748B', width=2.5)

    # 4. Buck OUT+ (5.15V) to NodeMCU VIN
    draw_wire([buck_out_plus, (71, 83), (71, 42), (96, 42)], '#F43F5E', width=3.0)

    # 5. NodeMCU 3V3 Logic Out to TB6612 VCC
    draw_wire([(96, 54), (98.5, 54), (98.5, 50), (63, 50)], '#FB923C', width=2.5)

    # 6. Motor Control Signals (NodeMCU Left Header -> TB6612 Left Header)
    # D1 (PWM Left) -> TB6612 PWMA
    draw_wire([(73, 62), (69, 62), (69, 56), tb_logic_pins["PWMA (Left Speed)"][:2]], '#38BDF8', width=2.0)
    # D2 (AIN1) -> TB6612 AIN1
    draw_wire([(73, 58), (67.5, 58), (67.5, 51), tb_logic_pins["AIN1 (Left Dir 1)"][:2]], '#4ADE80', width=2.0)
    # D3 (AIN2) -> TB6612 AIN2
    draw_wire([(73, 54), (66, 54), (66, 46), tb_logic_pins["AIN2 (Left Dir 2)"][:2]], '#FACC15', width=2.0)
    # D5 (BIN1) -> TB6612 BIN1
    draw_wire([(73, 50), (65, 50), (65, 36), tb_logic_pins["BIN1 (Right Dir 1)"][:2]], '#2DD4BF', width=2.0)
    # D6 (BIN2) -> TB6612 BIN2
    draw_wire([(73, 46), (64, 46), (64, 31), tb_logic_pins["BIN2 (Right Dir 2)"][:2]], '#E879F9', width=2.0)
    # D7 (PWMB) -> TB6612 PWMB
    draw_wire([(73, 42), (63, 42), (63, 26), tb_logic_pins["PWMB (Right Speed)"][:2]], '#818CF8', width=2.0)
    # D8 (STBY) -> TB6612 STBY (routed from right side)
    draw_wire([(96, 62), (97.5, 62), (97.5, 41), (65.5, 41), tb_logic_pins["STBY (Standby)"][:2]], '#C084FC', width=2.0)

    # 7. Motor Output Lines
    # Left Motor (AO1, AO2 -> Left TT Motor)
    draw_wire([tb_power_pins["AO1 (Left Motor +)"][:2], (65, 38), (65, 38), (25.5, 38), motor_left_p1], '#FCD34D', width=2.5)
    draw_wire([tb_power_pins["AO2 (Left Motor -)"][:2], (64, 33), (64, 33), (25.5, 33), motor_left_p2], '#F59E0B', width=2.5)
    # Right Motor (BO1, BO2 -> Right TT Motor)
    draw_wire([tb_power_pins["BO1 (Right Motor +)"][:2], (70, 27), (70, 22), motor_right_p1], '#38BDF8', width=2.5)
    draw_wire([tb_power_pins["BO2 (Right Motor -)"][:2], (68.5, 21), (68.5, 17), motor_right_p2], '#0284C7', width=2.5)

    # ==================== LEGEND & SAFETY CALLOUT BOXES ====================
    # Safety Banner (Bottom Left)
    draw_box(4, 2, 45, 9, '#1E293B', '#EF4444', "CRITICAL SAFETY & CALIBRATION RULES", "")
    ax.text(5, 7.5, "1. CALIBRATE BUCK FIRST: Trim LM2596 to exactly 5.15V DC BEFORE connecting NodeMCU VIN pin!", 
            fontsize=10, color='#FCA5A5', fontweight='bold', va='center')
    ax.text(5, 5.0, "2. COMMON STAR GROUND: Battery (-), LM2596 (-), NodeMCU GND & TB6612 GND MUST be tied together.", 
            fontsize=10, color='#FCD34D', va='center')
    ax.text(5, 2.5, "3. BOOT PIN SAFETY: GPIO 15 (D8) has pulldown on TB6612 STBY; GPIO 0 (D3) is high-Z.", 
            fontsize=10, color='#86EFAC', va='center')

    # Wire Legend (Bottom Right)
    draw_box(52, 2, 44, 9, '#1E293B', '#38BDF8', "WIRE COLOR CODE LEGEND", "")
    legend_items = [
        ("Red", "Battery (+) & 5.15V Logic", '#EF4444'),
        ("Black/Slate", "Common Ground (GND)", '#64748B'),
        ("Blue", "PWM Speed (PWMA: D1, PWMB: D7)", '#38BDF8'),
        ("Green/Yellow", "Left Direction (AIN1: D2, AIN2: D3)", '#4ADE80'),
        ("Cyan/Magenta", "Right Direction (BIN1: D5, BIN2: D6)", '#E879F9'),
        ("Purple/Orange", "Standby (STBY: D8) & 3.3V Logic", '#C084FC')
    ]
    for idx, (col_name, desc, hex_c) in enumerate(legend_items):
        row = idx // 2
        col = idx % 2
        lx = 54 + col * 21
        ly = 7.0 - row * 2.2
        plt.Circle((lx, ly), 0.7, color=hex_c, zorder=5)
        ax.add_patch(plt.Circle((lx, ly), 0.7, color=hex_c, zorder=5))
        ax.text(lx + 1.2, ly, f"{col_name}: {desc}", fontsize=9, color='#E2E8F0', va='center', zorder=5)

    plt.tight_layout()

    # Save to all target paths
    for p in output_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        plt.savefig(p, format='png', bbox_inches='tight', dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
        print(f"[SUCCESS] Wiring diagram saved to: {p}")
    plt.close()

if __name__ == "__main__":
    artifact_dir = r"C:\Users\suraj\.gemini\antigravity\brain\2a3e79a3-7671-431d-92eb-1b2bc379821c"
    paths = [
        os.path.join("docs", "wiring_diagram.png"),
        os.path.join(artifact_dir, "wiring_diagram.png")
    ]
    create_wiring_diagram(paths)
