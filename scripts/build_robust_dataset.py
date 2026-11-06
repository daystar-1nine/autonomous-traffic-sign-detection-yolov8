"""
Robust Multi-Style & Multi-Scale Dataset Generator for Autonomous AI Car
Features:
- Multi-Style Arrow Synthesis: Bold stem, Standard stem, Direct Horizontal, and Curved Bent arrows
- Color Hue Diversity: Deep Traffic Blue, Royal Blue, Electric Blue, Cyan Shift
- Motion & Focus Blur Synthesis: k=3, k=5 Gaussian-blurred variants of every template
- Orientation-locked: Strictly prevents horizontal flip confusion (fliplr=0.0)
- Multi-Scale: 0.12x (distant track signs) to 0.82x (close handheld / screen view)
- Position-Invariant: Center, Left, Right, Elevation variations
"""

import os
import glob
import random
import shutil
from pathlib import Path
import cv2
import numpy as np

# Seed for absolute reproducibility
random.seed(42)
np.random.seed(42)

CLASS_NAMES = ["left_turn", "straight_ahead", "right_turn", "dead_end", "no_entry", "stop"]

BLUE_SHADES = [
    (200, 90, 20),   # Standard Traffic Blue (BGR)
    (225, 110, 15),  # Electric Blue
    (170, 65, 25),   # Deep Navy Blue
    (215, 130, 10),  # Cyan-tinted Blue (Screen Backlight)
]

WHITE_RGBA = (255, 255, 255, 255)
RED_BGR = (30, 30, 220)

def create_vector_templates(out_dir: Path):
    """Generates rich multi-style vector sign graphics with diverse arrows, colors, and blur."""
    out_dir.mkdir(parents=True, exist_ok=True)
    size = 400
    center = (size // 2, size // 2)
    radius = 180

    templates = {i: [] for i in range(6)}

    def save_template(img, cid, name):
        p = out_dir / f"{name}.png"
        cv2.imwrite(str(p), img)
        templates[cid].append(p)

        # Also create a motion/focus blurred variant
        blur_k = random.choice([3, 5])
        blurred = cv2.GaussianBlur(img, (blur_k, blur_k), 0)
        pb = out_dir / f"{name}_blur{blur_k}.png"
        cv2.imwrite(str(pb), blurred)
        templates[cid].append(pb)

    # -------------------------------------------------------------
    # 0. LEFT TURN (Class 0) - Multi-Style
    # -------------------------------------------------------------
    for b_idx, blue in enumerate(BLUE_SHADES):
        # Style A: Standard Bent Arrow (stem 40px)
        img0_a = np.zeros((size, size, 4), dtype=np.uint8)
        cv2.circle(img0_a, center, radius, (*blue, 255), -1)
        cv2.circle(img0_a, center, radius, WHITE_RGBA, 10)
        cv2.rectangle(img0_a, (185, 200), (225, 310), WHITE_RGBA, -1)
        cv2.rectangle(img0_a, (140, 180), (225, 220), WHITE_RGBA, -1)
        cv2.fillPoly(img0_a, [np.array([[145, 140], [145, 260], [80, 200]], dtype=np.int32)], WHITE_RGBA)
        save_template(img0_a, 0, f"vec_0_left_std_b{b_idx}")

        # Style B: Bold Heavy-Duty Bent Arrow (stem 65px)
        img0_b = np.zeros((size, size, 4), dtype=np.uint8)
        cv2.circle(img0_b, center, radius, (*blue, 255), -1)
        cv2.circle(img0_b, center, radius, WHITE_RGBA, 12)
        cv2.rectangle(img0_b, (175, 190), (240, 325), WHITE_RGBA, -1)
        cv2.rectangle(img0_b, (135, 165), (240, 230), WHITE_RGBA, -1)
        cv2.fillPoly(img0_b, [np.array([[150, 120], [150, 275], [65, 198]], dtype=np.int32)], WHITE_RGBA)
        save_template(img0_b, 0, f"vec_0_left_bold_b{b_idx}")

        # Style C: Direct Horizontal Left Arrow
        img0_c = np.zeros((size, size, 4), dtype=np.uint8)
        cv2.circle(img0_c, center, radius, (*blue, 255), -1)
        cv2.circle(img0_c, center, radius, WHITE_RGBA, 12)
        cv2.rectangle(img0_c, (140, 172), (300, 228), WHITE_RGBA, -1)
        cv2.fillPoly(img0_c, [np.array([[155, 130], [155, 270], [70, 200]], dtype=np.int32)], WHITE_RGBA)
        save_template(img0_c, 0, f"vec_0_left_horiz_b{b_idx}")

    # -------------------------------------------------------------
    # 1. STRAIGHT AHEAD (Class 1) - Multi-Style
    # -------------------------------------------------------------
    for b_idx, blue in enumerate(BLUE_SHADES):
        # Style A: Standard Vertical Arrow (stem 40px)
        img1_a = np.zeros((size, size, 4), dtype=np.uint8)
        cv2.circle(img1_a, center, radius, (*blue, 255), -1)
        cv2.circle(img1_a, center, radius, WHITE_RGBA, 10)
        cv2.rectangle(img1_a, (180, 180), (220, 320), WHITE_RGBA, -1)
        cv2.fillPoly(img1_a, [np.array([[130, 185], [270, 185], [200, 80]], dtype=np.int32)], WHITE_RGBA)
        save_template(img1_a, 1, f"vec_1_straight_std_b{b_idx}")

        # Style B: Bold Highway Vertical Arrow (stem 68px, wide head)
        img1_b = np.zeros((size, size, 4), dtype=np.uint8)
        cv2.circle(img1_b, center, radius, (*blue, 255), -1)
        cv2.circle(img1_b, center, radius, WHITE_RGBA, 12)
        cv2.rectangle(img1_b, (166, 170), (234, 330), WHITE_RGBA, -1)
        cv2.fillPoly(img1_b, [np.array([[105, 180], [295, 180], [200, 70]], dtype=np.int32)], WHITE_RGBA)
        save_template(img1_b, 1, f"vec_1_straight_bold_b{b_idx}")

        # Style C: ISO Sharp Arrowhead
        img1_c = np.zeros((size, size, 4), dtype=np.uint8)
        cv2.circle(img1_c, center, radius, (*blue, 255), -1)
        cv2.circle(img1_c, center, radius, WHITE_RGBA, 10)
        cv2.rectangle(img1_c, (175, 195), (225, 325), WHITE_RGBA, -1)
        cv2.fillPoly(img1_c, [np.array([[115, 205], [285, 205], [200, 65]], dtype=np.int32)], WHITE_RGBA)
        save_template(img1_c, 1, f"vec_1_straight_iso_b{b_idx}")

    # -------------------------------------------------------------
    # 2. RIGHT TURN (Class 2) - Multi-Style
    # -------------------------------------------------------------
    for b_idx, blue in enumerate(BLUE_SHADES):
        # Style A: Standard Bent Arrow (stem 40px)
        img2_a = np.zeros((size, size, 4), dtype=np.uint8)
        cv2.circle(img2_a, center, radius, (*blue, 255), -1)
        cv2.circle(img2_a, center, radius, WHITE_RGBA, 10)
        cv2.rectangle(img2_a, (175, 200), (215, 310), WHITE_RGBA, -1)
        cv2.rectangle(img2_a, (175, 180), (260, 220), WHITE_RGBA, -1)
        cv2.fillPoly(img2_a, [np.array([[255, 140], [255, 260], [320, 200]], dtype=np.int32)], WHITE_RGBA)
        save_template(img2_a, 2, f"vec_2_right_std_b{b_idx}")

        # Style B: Bold Heavy-Duty Bent Arrow (stem 65px)
        img2_b = np.zeros((size, size, 4), dtype=np.uint8)
        cv2.circle(img2_b, center, radius, (*blue, 255), -1)
        cv2.circle(img2_b, center, radius, WHITE_RGBA, 12)
        cv2.rectangle(img2_b, (160, 190), (225, 325), WHITE_RGBA, -1)
        cv2.rectangle(img2_b, (160, 165), (265, 230), WHITE_RGBA, -1)
        cv2.fillPoly(img2_b, [np.array([[250, 120], [250, 275], [335, 198]], dtype=np.int32)], WHITE_RGBA)
        save_template(img2_b, 2, f"vec_2_right_bold_b{b_idx}")

        # Style C: Direct Horizontal Right Arrow
        img2_c = np.zeros((size, size, 4), dtype=np.uint8)
        cv2.circle(img2_c, center, radius, (*blue, 255), -1)
        cv2.circle(img2_c, center, radius, WHITE_RGBA, 12)
        cv2.rectangle(img2_c, (100, 172), (260, 228), WHITE_RGBA, -1)
        cv2.fillPoly(img2_c, [np.array([[245, 130], [245, 270], [330, 200]], dtype=np.int32)], WHITE_RGBA)
        save_template(img2_c, 2, f"vec_2_right_horiz_b{b_idx}")

    # -------------------------------------------------------------
    # 3. DEAD END (Class 3)
    # -------------------------------------------------------------
    for b_idx, blue in enumerate(BLUE_SHADES[:2]):
        img3 = np.zeros((size, size, 4), dtype=np.uint8)
        cv2.rectangle(img3, (30, 30), (370, 370), (*blue, 255), -1)
        cv2.rectangle(img3, (30, 30), (370, 370), WHITE_RGBA, 10)
        cv2.rectangle(img3, (175, 150), (225, 325), WHITE_RGBA, -1)
        cv2.rectangle(img3, (115, 110), (285, 155), (*RED_BGR, 255), -1)
        cv2.rectangle(img3, (115, 110), (285, 155), WHITE_RGBA, 4)
        save_template(img3, 3, f"vec_3_dead_end_b{b_idx}")

    # -------------------------------------------------------------
    # 4. NO ENTRY (Class 4)
    # -------------------------------------------------------------
    for red_val in [(30, 30, 220), (20, 20, 240)]:
        img4 = np.zeros((size, size, 4), dtype=np.uint8)
        cv2.circle(img4, center, radius, (*red_val, 255), -1)
        cv2.circle(img4, center, radius, WHITE_RGBA, 10)
        cv2.rectangle(img4, (80, 172), (320, 228), WHITE_RGBA, -1)
        save_template(img4, 4, f"vec_4_no_entry_r{red_val[2]}")

    # -------------------------------------------------------------
    # 5. STOP SIGN (Class 5)
    # -------------------------------------------------------------
    for red_val in [(30, 30, 220), (20, 20, 240)]:
        img5 = np.zeros((size, size, 4), dtype=np.uint8)
        angles = [np.pi/8 + i * np.pi/4 for i in range(8)]
        oct_pts = np.array([[int(center[0] + radius * np.cos(a)), int(center[1] + radius * np.sin(a))] for a in angles], dtype=np.int32)
        cv2.fillPoly(img5, [oct_pts], (*red_val, 255))
        cv2.polylines(img5, [oct_pts], True, WHITE_RGBA, 10)
        inner_pts = np.array([[int(center[0] + (radius - 16) * np.cos(a)), int(center[1] + (radius - 16) * np.sin(a))] for a in angles], dtype=np.int32)
        cv2.polylines(img5, [inner_pts], True, WHITE_RGBA, 4)
        font = cv2.FONT_HERSHEY_TRIPLEX
        ts = cv2.getTextSize('STOP', font, 2.5, 6)[0]
        tx = center[0] - ts[0] // 2
        ty = center[1] + ts[1] // 2
        cv2.putText(img5, 'STOP', (tx, ty), font, 2.5, WHITE_RGBA, 7, cv2.LINE_AA)
        save_template(img5, 5, f"vec_5_stop_r{red_val[2]}")

    print(f"[INFO] Created {sum(len(v) for v in templates.values())} vector templates across 6 classes.")
    return templates


def overlay_sign_on_bg(bg_img, sign_path, box_rect, angle=0.0):
    """Blends a transparent sign onto a background canvas with rotation."""
    x, y, w, h = box_rect
    sign = cv2.imread(str(sign_path), cv2.IMREAD_UNCHANGED)
    if sign is None or sign.shape[2] != 4:
        return bg_img, None

    # Rotate sign if needed
    if abs(angle) > 0.5:
        sh, sw = sign.shape[:2]
        M = cv2.getRotationMatrix2D((sw / 2, sh / 2), angle, 1.0)
        sign = cv2.warpAffine(sign, M, (sw, sh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

    # Resize to target box
    sign_resized = cv2.resize(sign, (w, h), interpolation=cv2.INTER_AREA)

    # Clipping boundaries
    H, W = bg_img.shape[:2]
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(W, x + w)
    y2 = min(H, y + h)

    if x2 <= x1 or y2 <= y1:
        return bg_img, None

    sx1 = x1 - x
    sy1 = y1 - y
    sx2 = sx1 + (x2 - x1)
    sy2 = sy1 + (y2 - y1)

    crop_sign = sign_resized[sy1:sy2, sx1:sx2]
    alpha = (crop_sign[:, :, 3] / 255.0)[:, :, np.newaxis]
    rgb = crop_sign[:, :, :3]

    bg_region = bg_img[y1:y2, x1:x2].astype(np.float32)
    blended = (rgb * alpha + bg_region * (1.0 - alpha)).astype(np.uint8)
    bg_img[y1:y2, x1:x2] = blended

    return bg_img, (x1, y1, x2, y2)


def generate_robust_split(split_name: str, count_per_class: int, templates: dict, clean_bgs: list, output_dir: Path):
    """Synthesizes position, scale, and background invariant images."""
    img_dir = output_dir / split_name / "images"
    lbl_dir = output_dir / split_name / "labels"
    img_dir.mkdir(parents=True, exist_ok=True)
    lbl_dir.mkdir(parents=True, exist_ok=True)

    canvas_size = 640

    for cid, cname in enumerate(CLASS_NAMES):
        for s in range(count_per_class):
            # Select background: 50% Clean Solid / Screen tints, 50% Natural environments
            bg_roll = random.random()
            if bg_roll < 0.25:
                # White/off-white (laptop screen simulation)
                tint = random.randint(235, 255)
                bg = np.ones((canvas_size, canvas_size, 3), dtype=np.uint8) * tint
            elif bg_roll < 0.45:
                # Dark Road / Charcoal screen
                dark_tint = random.randint(15, 45)
                bg = np.ones((canvas_size, canvas_size, 3), dtype=np.uint8) * dark_tint
            else:
                # Natural environment background
                bg_file = random.choice(clean_bgs)
                bg_raw = cv2.imread(bg_file)
                if bg_raw is not None:
                    bg = cv2.resize(bg_raw, (canvas_size, canvas_size))
                else:
                    bg = np.ones((canvas_size, canvas_size, 3), dtype=np.uint8) * random.randint(100, 200)

            # Scale selection: 0.12 to 0.80
            scale_roll = random.random()
            if scale_roll < 0.35:
                scale = random.uniform(0.12, 0.25) # Small / Far
            elif scale_roll < 0.75:
                scale = random.uniform(0.26, 0.55) # Medium
            else:
                scale = random.uniform(0.56, 0.80) # Large / Close

            sign_w = int(canvas_size * scale)
            sign_h = sign_w

            # Position selection:
            # 50% Centered (handheld / direct phone view)
            # 25% Left side of roadway
            # 25% Right side of roadway
            pos_roll = random.random()
            if pos_roll < 0.50:
                cx = random.uniform(0.40, 0.60)
                cy = random.uniform(0.40, 0.60)
            elif pos_roll < 0.75:
                cx = random.uniform(0.15, 0.38)
                cy = random.uniform(0.25, 0.70)
            else:
                cx = random.uniform(0.62, 0.85)
                cy = random.uniform(0.25, 0.70)

            px = int(cx * canvas_size - sign_w / 2)
            py = int(cy * canvas_size - sign_h / 2)

            # Pick template from multi-style pool
            tmpl_path = random.choice(templates[cid])
            # Strict controlled tilt: +/- 10 degrees (preserves arrow semantics)
            rot_angle = random.uniform(-10, 10)

            bg, bbox = overlay_sign_on_bg(bg, tmpl_path, (px, py, sign_w, sign_h), angle=rot_angle)
            if bbox is None:
                continue

            x1, y1, x2, y2 = bbox
            box_w = x2 - x1
            box_h = y2 - y1

            if box_w < 10 or box_h < 10:
                continue

            norm_cx = (x1 + box_w / 2.0) / canvas_size
            norm_cy = (y1 + box_h / 2.0) / canvas_size
            norm_w = box_w / canvas_size
            norm_h = box_h / canvas_size

            out_img_name = f"multi_{split_name}_{cname}_{s:04d}.jpg"
            out_lbl_name = f"multi_{split_name}_{cname}_{s:04d}.txt"

            cv2.imwrite(str(img_dir / out_img_name), bg)
            with open(lbl_dir / out_lbl_name, "w") as fp:
                fp.write(f"{cid} {norm_cx:.6f} {norm_cy:.6f} {norm_w:.6f} {norm_h:.6f}\n")

    print(f"[SUCCESS] {split_name} split generated with {len(list(img_dir.glob('*.jpg')))} images.")


def copy_original_balanced(src_split: str, dst_split: str, count_per_class: int, output_dir: Path):
    """Copies a balanced subset of original dataset."""
    dst_img_dir = output_dir / dst_split / "images"
    dst_lbl_dir = output_dir / dst_split / "labels"
    dst_img_dir.mkdir(parents=True, exist_ok=True)
    dst_lbl_dir.mkdir(parents=True, exist_ok=True)

    counts = {i: 0 for i in range(6)}
    lbl_files = glob.glob(f"dataset/{src_split}/labels/*.txt")
    random.shuffle(lbl_files)

    for lf in lbl_files:
        with open(lf) as f:
            lines = f.readlines()
        if len(lines) == 1:
            cid = int(lines[0].strip().split()[0])
            if counts[cid] < count_per_class:
                img_name = Path(lf).name.replace('.txt', '.jpg')
                src_img = Path(f"dataset/{src_split}/images/{img_name}")
                if src_img.is_file():
                    shutil.copy(str(src_img), str(dst_img_dir / f"orig_{src_split}_{img_name}"))
                    shutil.copy(lf, str(dst_lbl_dir / f"orig_{src_split}_{Path(lf).name}"))
                    counts[cid] += 1

    print(f"[INFO] Copied balanced original samples for {dst_split}: {counts}")


def main():
    root = Path(".")
    temp_dir = root / "dataset_augmented"
    output_dir = root / "dataset_robust"

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Prepare Rich Multi-Style Templates
    templates = create_vector_templates(temp_dir / "vector_signs")

    # 2. Collect Background Pool
    clean_bg_pool = glob.glob("dataset/train/images/*.jpg")[:1500]

    # 3. Generate Augmented Multi-Scale Training Split: 450 per class = 2700 images
    generate_robust_split("train", 450, templates, clean_bg_pool, output_dir)
    # Copy 150 per class original train samples = 900 images -> Total Train: 3600 images
    copy_original_balanced("train", "train", 150, output_dir)

    # 4. Generate Augmented Multi-Scale Validation Split: 70 per class = 420 images
    generate_robust_split("valid", 70, templates, clean_bg_pool, output_dir)
    # Copy 30 per class original valid samples = 180 images -> Total Val: 600 images
    copy_original_balanced("valid", "valid", 30, output_dir)

    # 5. Write dataset_robust/data.yaml
    yaml_content = f"""# Robust Multi-Scale & Multi-Style Traffic Signs Dataset
path: {str(output_dir.resolve()).replace('\\', '/')}
train: train/images
val: valid/images

nc: 6

names:
  0: left_turn
  1: straight_ahead
  2: right_turn
  3: dead_end
  4: no_entry
  5: stop
"""
    with open(output_dir / "data.yaml", "w") as f:
        f.write(yaml_content)

    print("\n=======================================================")
    print(f"[COMPLETE] Multi-style dataset created at: {output_dir.resolve()}")
    print("=======================================================")


if __name__ == "__main__":
    main()
