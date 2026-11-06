"""
Robust Multi-Scale Dataset Generator for Autonomous AI Car Traffic Sign Detection
Generates position-invariant, multi-scale training and validation datasets to eliminate
spatial bias and enable 100% detection of real, centered, and handheld/screen signs.
"""

import os
import glob
import random
import shutil
from pathlib import Path
import cv2
import numpy as np

# Seed for reproducibility
random.seed(42)
np.random.seed(42)

CLASS_NAMES = ["left_turn", "straight_ahead", "right_turn", "dead_end", "no_entry", "stop"]

def create_vector_templates(out_dir: Path):
    """Generates crisp vector sign graphics with alpha transparency."""
    out_dir.mkdir(parents=True, exist_ok=True)
    size = 400
    center = (size // 2, size // 2)
    radius = 180

    templates = {i: [] for i in range(6)}

    # 0: left_turn
    img0 = np.zeros((size, size, 4), dtype=np.uint8)
    cv2.circle(img0, center, radius, (200, 90, 20, 255), -1)
    cv2.circle(img0, center, radius, (255, 255, 255, 255), 10)
    cv2.rectangle(img0, (185, 200), (225, 310), (255, 255, 255, 255), -1)
    cv2.rectangle(img0, (140, 180), (225, 220), (255, 255, 255, 255), -1)
    cv2.fillPoly(img0, [np.array([[145, 140], [145, 260], [80, 200]], dtype=np.int32)], (255, 255, 255, 255))
    p0 = out_dir / 'vec_0_left_turn.png'
    cv2.imwrite(str(p0), img0)
    templates[0].append(p0)

    # 1: straight_ahead
    img1 = np.zeros((size, size, 4), dtype=np.uint8)
    cv2.circle(img1, center, radius, (200, 90, 20, 255), -1)
    cv2.circle(img1, center, radius, (255, 255, 255, 255), 10)
    cv2.rectangle(img1, (185, 180), (215, 320), (255, 255, 255, 255), -1)
    cv2.fillPoly(img1, [np.array([[140, 185], [260, 185], [200, 90]], dtype=np.int32)], (255, 255, 255, 255))
    p1 = out_dir / 'vec_1_straight_ahead.png'
    cv2.imwrite(str(p1), img1)
    templates[1].append(p1)

    # 2: right_turn
    img2 = np.zeros((size, size, 4), dtype=np.uint8)
    cv2.circle(img2, center, radius, (200, 90, 20, 255), -1)
    cv2.circle(img2, center, radius, (255, 255, 255, 255), 10)
    cv2.rectangle(img2, (175, 200), (215, 310), (255, 255, 255, 255), -1)
    cv2.rectangle(img2, (175, 180), (260, 220), (255, 255, 255, 255), -1)
    cv2.fillPoly(img2, [np.array([[255, 140], [255, 260], [320, 200]], dtype=np.int32)], (255, 255, 255, 255))
    p2 = out_dir / 'vec_2_right_turn.png'
    cv2.imwrite(str(p2), img2)
    templates[2].append(p2)

    # 3: dead_end
    img3 = np.zeros((size, size, 4), dtype=np.uint8)
    cv2.rectangle(img3, (30, 30), (370, 370), (200, 90, 20, 255), -1)
    cv2.rectangle(img3, (30, 30), (370, 370), (255, 255, 255, 255), 10)
    cv2.rectangle(img3, (180, 150), (220, 320), (255, 255, 255, 255), -1)
    cv2.rectangle(img3, (120, 110), (280, 150), (30, 30, 220, 255), -1)
    cv2.rectangle(img3, (120, 110), (280, 150), (255, 255, 255, 255), 4)
    p3 = out_dir / 'vec_3_dead_end.png'
    cv2.imwrite(str(p3), img3)
    templates[3].append(p3)

    # 4: no_entry
    img4 = np.zeros((size, size, 4), dtype=np.uint8)
    cv2.circle(img4, center, radius, (30, 30, 220, 255), -1)
    cv2.circle(img4, center, radius, (255, 255, 255, 255), 10)
    cv2.rectangle(img4, (80, 175), (320, 225), (255, 255, 255, 255), -1)
    p4 = out_dir / 'vec_4_no_entry.png'
    cv2.imwrite(str(p4), img4)
    templates[4].append(p4)

    # 5: stop
    img5 = np.zeros((size, size, 4), dtype=np.uint8)
    angles = [np.pi/8 + i * np.pi/4 for i in range(8)]
    oct_pts = np.array([[int(center[0] + radius * np.cos(a)), int(center[1] + radius * np.sin(a))] for a in angles], dtype=np.int32)
    cv2.fillPoly(img5, [oct_pts], (30, 30, 220, 255))
    cv2.polylines(img5, [oct_pts], True, (255, 255, 255, 255), 10)
    inner_radius = radius - 15
    inner_pts = np.array([[int(center[0] + inner_radius * np.cos(a)), int(center[1] + inner_radius * np.sin(a))] for a in angles], dtype=np.int32)
    cv2.polylines(img5, [inner_pts], True, (255, 255, 255, 255), 4)
    font = cv2.FONT_HERSHEY_TRIPLEX
    ts = cv2.getTextSize('STOP', font, 2.5, 6)[0]
    tx = center[0] - ts[0] // 2
    ty = center[1] + ts[1] // 2
    cv2.putText(img5, 'STOP', (tx, ty), font, 2.5, (255, 255, 255, 255), 7, cv2.LINE_AA)
    p5 = out_dir / 'vec_5_stop.png'
    cv2.imwrite(str(p5), img5)
    templates[5].append(p5)

    return templates


def extract_real_crops_with_alpha(out_dir: Path, templates: dict):
    """Extracts diverse natural crops from dataset/train and adds alpha masks."""
    out_dir.mkdir(parents=True, exist_ok=True)
    counts = {i: 0 for i in range(6)}
    target_per_class = 20

    lbl_files = glob.glob('dataset/train/labels/*.txt')
    random.shuffle(lbl_files)

    for lbl_file in lbl_files:
        with open(lbl_file) as f:
            lines = f.readlines()
        for line in lines:
            parts = line.strip().split()
            if len(parts) == 5:
                cid = int(parts[0])
                if counts[cid] < target_per_class:
                    cx, cy, bw, bh = [float(x) for x in parts[1:]]
                    img_file = lbl_file.replace('labels', 'images').replace('.txt', '.jpg')
                    img = cv2.imread(img_file)
                    if img is not None:
                        h, w, _ = img.shape
                        x1 = max(0, int((cx - bw/2) * w))
                        y1 = max(0, int((cy - bh/2) * h))
                        x2 = min(w, int((cx + bw/2) * w))
                        y2 = min(h, int((cy + bh/2) * h))
                        crop = img[y1:y2, x1:x2]
                        ch, cw, _ = crop.shape
                        if ch > 25 and cw > 25:
                            alpha = np.zeros((ch, cw), dtype=np.uint8)
                            if cid in [0, 1, 2, 4]:
                                cv2.ellipse(alpha, (cw//2, ch//2), (cw//2 - 2, ch//2 - 2), 0, 0, 360, 255, -1)
                            elif cid == 5:
                                angles = [np.pi/8 + i * np.pi/4 for i in range(8)]
                                pts = np.array([[int(cw/2 + (cw/2 - 2)*np.cos(a)), int(ch/2 + (ch/2 - 2)*np.sin(a))] for a in angles], dtype=np.int32)
                                cv2.fillPoly(alpha, [pts], 255)
                            else:
                                cv2.rectangle(alpha, (2, 2), (cw - 3, ch - 3), 255, -1)

                            crop_4ch = np.dstack([crop, alpha])
                            save_path = out_dir / f'real_crop_{cid}_{counts[cid]}.png'
                            cv2.imwrite(str(save_path), crop_4ch)
                            templates[cid].append(save_path)
                            counts[cid] += 1

    # Also add the real test stop sign if available
    real_stop = Path('05_PYTHON_TOOLS/test_images/stop_sign.jpg')
    if real_stop.is_file():
        im = cv2.imread(str(real_stop))
        if im is not None:
            rh, rw, _ = im.shape
            alpha = np.zeros((rh, rw), dtype=np.uint8)
            angles = [np.pi/8 + i * np.pi/4 for i in range(8)]
            pts = np.array([[int(rw/2 + (rw/2 - 5)*np.cos(a)), int(rh/2 + (rh/2 - 5)*np.sin(a))] for a in angles], dtype=np.int32)
            cv2.fillPoly(alpha, [pts], 255)
            stop_4ch = np.dstack([im, alpha])
            p_real_stop = out_dir / 'real_stop_test_img.png'
            cv2.imwrite(str(p_real_stop), stop_4ch)
            templates[5].append(p_real_stop)

    print(f"[INFO] Templates collected per class: {[len(templates[i]) for i in range(6)]}")


def overlay_sign_on_bg(bg, template_path, target_box, angle=0):
    """
    Overlays a transparent sign on bg inside target_box: (x, y, w, h).
    Applies optional rotation, color jitter, and returns updated bg and exact bbox (x1, y1, x2, y2).
    """
    x, y, w, h = target_box
    ov = cv2.imread(str(template_path), cv2.IMREAD_UNCHANGED)
    if ov is None:
        return bg, None

    ov_resized = cv2.resize(ov, (w, h), interpolation=cv2.INTER_LINEAR)

    # Optional slight rotation
    if angle != 0:
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        ov_resized = cv2.warpAffine(ov_resized, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

    # Optional subtle brightness/contrast variation
    alpha_gain = random.uniform(0.85, 1.15)
    beta_bias = random.randint(-15, 15)
    rgb = ov_resized[:, :, :3].astype(np.float32) * alpha_gain + beta_bias
    ov_resized[:, :, :3] = np.clip(rgb, 0, 255).astype(np.uint8)

    y1, y2 = max(0, y), min(bg.shape[0], y + h)
    x1, x2 = max(0, x), min(bg.shape[1], x + w)

    oy1, oy2 = max(0, -y), h - max(0, (y + h) - bg.shape[0])
    ox1, ox2 = max(0, -x), w - max(0, (x + w) - bg.shape[1])

    if y1 >= y2 or x1 >= x2:
        return bg, None

    patch = ov_resized[oy1:oy2, ox1:ox2]
    if patch.shape[2] == 4:
        alpha = (patch[:, :, 3] / 255.0)[:, :, np.newaxis]
        bg[y1:y2, x1:x2] = (alpha * patch[:, :, :3] + (1.0 - alpha) * bg[y1:y2, x1:x2]).astype(np.uint8)
    else:
        bg[y1:y2, x1:x2] = patch[:, :, :3]

    return bg, (x1, y1, x2, y2)


def generate_robust_split(
    split_name: str,
    num_samples_per_class: int,
    templates: dict,
    clean_bg_pool: list,
    output_dir: Path
):
    img_dir = output_dir / split_name / "images"
    lbl_dir = output_dir / split_name / "labels"
    img_dir.mkdir(parents=True, exist_ok=True)
    lbl_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[INFO] Generating {split_name} split: {num_samples_per_class} samples per class ({num_samples_per_class * 6} total)...")

    sample_id = 0
    canvas_size = 640

    for cid in range(6):
        cname = CLASS_NAMES[cid]
        for s in range(num_samples_per_class):
            sample_id += 1

            # 1. Background selection: 60% real background crop, 20% room/desk mockup, 20% plain monitor/paper
            bg_type = random.random()
            if bg_type < 0.60 and len(clean_bg_pool) > 0:
                bg_path = random.choice(clean_bg_pool)
                raw_bg = cv2.imread(bg_path)
                if raw_bg is not None:
                    # Take clean left half or top half to avoid original corner sign
                    if random.random() < 0.5:
                        bg_crop = raw_bg[:, :380]
                    else:
                        bg_crop = raw_bg[:350, :]
                    bg = cv2.resize(bg_crop, (canvas_size, canvas_size))
                else:
                    bg = np.full((canvas_size, canvas_size, 3), random.randint(80, 160), dtype=np.uint8)
            elif bg_type < 0.80:
                # Desktop / Indoor neutral texture
                base_color = random.randint(40, 220)
                noise = np.random.randint(-20, 20, (canvas_size, canvas_size, 3), dtype=np.int16)
                bg = np.clip(base_color + noise, 0, 255).astype(np.uint8)
            else:
                # White/off-white paper or screen test card
                paper_val = random.randint(220, 250)
                bg = np.full((canvas_size, canvas_size, 3), paper_val, dtype=np.uint8)
                # Maybe add a screen/card border
                if random.random() < 0.5:
                    cv2.rectangle(bg, (40, 40), (600, 600), (30, 30, 30), 4)

            # 2. Scale selection:
            # 40% Large / Close-up (user holding phone or looking at screen)
            # 35% Mid-range
            # 25% Distant
            scale_roll = random.random()
            if scale_roll < 0.40:
                scale_fraction = random.uniform(0.40, 0.75)
            elif scale_roll < 0.75:
                scale_fraction = random.uniform(0.20, 0.40)
            else:
                scale_fraction = random.uniform(0.12, 0.20)

            sign_w = int(canvas_size * scale_fraction)
            sign_h = int(sign_w * random.uniform(0.95, 1.25))

            # 3. Position selection:
            # 50% Centered (where users show signs)
            # 25% Left
            # 25% Right
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

            # Pick template
            tmpl_path = random.choice(templates[cid])
            rot_angle = random.uniform(-12, 12)

            bg, bbox = overlay_sign_on_bg(bg, tmpl_path, (px, py, sign_w, sign_h), angle=rot_angle)
            if bbox is None:
                continue

            x1, y1, x2, y2 = bbox
            box_w = x2 - x1
            box_h = y2 - y1

            # Validate box
            if box_w < 10 or box_h < 10:
                continue

            # Convert to normalized YOLO format
            norm_cx = (x1 + box_w / 2.0) / canvas_size
            norm_cy = (y1 + box_h / 2.0) / canvas_size
            norm_w = box_w / canvas_size
            norm_h = box_h / canvas_size

            out_img_name = f"aug_{split_name}_{cname}_{s:04d}.jpg"
            out_lbl_name = f"aug_{split_name}_{cname}_{s:04d}.txt"

            cv2.imwrite(str(img_dir / out_img_name), bg)
            with open(lbl_dir / out_lbl_name, "w") as fp:
                fp.write(f"{cid} {norm_cx:.6f} {norm_cy:.6f} {norm_w:.6f} {norm_h:.6f}\n")

    print(f"[SUCCESS] {split_name} split generated with {len(list(img_dir.glob('*.jpg')))} images.")


def copy_original_balanced(src_split: str, dst_split: str, count_per_class: int, output_dir: Path):
    """Copies a balanced subset of original dataset to maintain original roadway detection."""
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

    # 1. Prepare Templates
    templates = create_vector_templates(temp_dir / "vector_signs")
    extract_real_crops_with_alpha(temp_dir / "real_crops", templates)

    # 2. Collect Clean Background Pool
    clean_bg_pool = glob.glob("dataset/train/images/*.jpg")[:1500]

    # 3. Generate Augmented Multi-Scale Training Split: 400 per class = 2400 images
    generate_robust_split("train", 400, templates, clean_bg_pool, output_dir)
    # Copy 200 per class original train samples = 1200 images -> Total Train: 3600 images
    copy_original_balanced("train", "train", 200, output_dir)

    # 4. Generate Augmented Multi-Scale Validation Split: 60 per class = 360 images
    generate_robust_split("valid", 60, templates, clean_bg_pool, output_dir)
    # Copy 40 per class original valid samples = 240 images -> Total Val: 600 images
    copy_original_balanced("valid", "valid", 40, output_dir)

    # 5. Write dataset_robust/data.yaml
    yaml_content = f"""# Robust Multi-Scale Traffic Signs Dataset
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
    print(f"[COMPLETE] Robust multi-scale dataset created successfully at: {output_dir.resolve()}")
    print("=======================================================")


if __name__ == "__main__":
    main()
