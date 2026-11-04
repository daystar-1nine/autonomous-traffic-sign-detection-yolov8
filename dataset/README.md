# Traffic Signs Dataset - YOLOv8 to YOLOv11 Benchmarking

## 📦 Dataset Information

This dataset contains images of traffic signs captured in a FIRA-based urban simulation scenario for autonomous vehicle competitions at 1:10 scale.

### 🚦 Traffic Signs Classes (6 total)

**⚠️ IMPORTANT: Class IDs match the order defined in the research article**

| Class ID | Sign Name | Description | Emoji |
|----------|-----------|-------------|-------|
| 0 | Left Turn | Turn left signal | 🔄 |
| 1 | Straight Ahead | Go straight signal | ⬆️ |
| 2 | Right Turn | Turn right signal | 🔃 |
| 3 | Dead End | Dead end / No through road | 🚫 |
| 4 | No Entry | Do not enter | ⛔ |
| 5 | Stop | Stop sign | 🛑 |

### 📊 Dataset Statistics

- **Total Images**: 6,000
- **Training Set**: 4,200 images (70%)
- **Validation Set**: 1,200 images (20%)
- **Test Set**: 600 images (10%)
- **Image Format**: JPG
- **Annotation Format**: YOLO format (.txt)
- **Image Resolution**: Varies (captured from Intel RealSense D435i)
- **Classes**: 6 traffic signs

### 📁 Directory Structure

```
dataset/
│
├── train/
│   ├── images/
│   │   ├── img_0001.jpg
│   │   ├── img_0002.jpg
│   │   └── ...
│   └── labels/
│       ├── img_0001.txt
│       ├── img_0002.txt
│       └── ...
│
├── valid/
│   ├── images/
│   └── labels/
│
├── test/
│   ├── images/
│   └── labels/
│
├── data.yaml              # Dataset configuration for YOLO
└── classes.txt            # Class names

```

### 📝 YOLO Annotation Format

Each `.txt` file contains annotations in YOLO format:

```
<class_id> <x_center> <y_center> <width> <height>
```

Where:
- `class_id`: Integer from 0-5 (see table above)
- `x_center, y_center`: Normalized center coordinates (0-1)
- `width, height`: Normalized bounding box dimensions (0-1)

Example:
```
5 0.512 0.345 0.156 0.234
```
(Stop sign [class 5] at center (0.512, 0.345) with size 0.156×0.234)

### 🎥 Data Acquisition

- **Camera**: Intel RealSense D435i
- **Environment**: Indoor FIRA-based urban simulation track
- **Lighting**: Controlled indoor lighting
- **Distance**: Varied (0.5m - 3.0m from camera)
- **Angles**: Multiple viewing angles
- **Conditions**: Various lighting and positioning conditions

### 🏷️ Annotation Tool

Images were annotated using **CVAT (Computer Vision Annotation Tool)**

### 🔧 Configuration File (data.yaml)

```yaml
path: ./dataset  # dataset root dir
train: train/images
val: valid/images
test: test/images

# Classes (as defined in the article)
names:
  0: left_turn
  1: straight_ahead
  2: right_turn
  3: dead_end
  4: no_entry
  5: stop
```

### 🚀 Usage

#### 1. Clone the repository

```bash
git clone https://github.com/rrevelesm/Articulos-Benchmarking-YOLOv8-to-YOLOv11.git
cd Articulos-Benchmarking-YOLOv8-to-YOLOv11
```

#### 2. Training with YOLOv8-v11

```python
from ultralytics import YOLO

# Load a model
model = YOLO('yolov8n.pt')  # or yolov10n.pt, yolov11n.pt

# Train the model
results = model.train(
    data='data.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    device=0
)
```

#### 3. Inference

```python
# Load trained model
model = YOLO('path/to/best.pt')

# Run inference
results = model('path/to/test/image.jpg')

# Display results
results[0].show()
```

### 📊 Benchmark Results

This dataset was used to benchmark the following models:

| Model | mAP@50-95 | FPS | Params | GFLOPs |
|-------|-----------|-----|--------|--------|
| YOLOv8n | [TBF] | [TBF] | 3.2M | 8.7 |
| YOLOv8s | [TBF] | [TBF] | 11.2M | 28.6 |
| YOLOv8m | [TBF] | [TBF] | 25.9M | 78.9 |
| YOLOv10b | [TBF] | [TBF] | [TBF] | [TBF] |
| YOLOv11n | [TBF] | [TBF] | [TBF] | [TBF] |

For complete results, please refer to the full paper.

### 📄 Related Publication

This dataset accompanies the research paper:

**"Benchmarking YOLOv8 to YOLOv11 Architectures for Real-Time Traffic Sign Recognition in Embedded 1:10 Scale Autonomous Vehicles"**

Published in: *Technologies*, MDPI, 2025

Authors: Rafael Reveles-Martínez, Hamurabi Gamboa-Rosales, et al.

### 📜 License

This dataset is released under [LICENSE TO BE SPECIFIED - suggest CC BY 4.0].

### 🙏 Acknowledgments

This work was supported by:
- Secretaría de Investigación y Posgrado (SIP-IPN)
- Instituto Politécnico Nacional (IPN)
- Universidad Autónoma de Zacatecas (UAZ)

### 📧 Contact

For questions or issues regarding this dataset:

- Rafael Reveles-Martínez: rrevelesm@ipn.mx
- José M. Celaya-Padilla: jose.celaya@uaz.edu.mx

### 🐛 Issues

If you find any issues with the dataset, please open an issue in this repository.

---

**Citation**:

```bibtex
@dataset{reveles2025traffic,
  title={Traffic Signs Dataset for YOLOv8-YOLOv11 Benchmarking},
  author={Reveles-Mart{\'i}nez, Rafael and Gamboa-Rosales, Hamurabi and others},
  year={2025},
  publisher={GitHub},
  url={https://github.com/rrevelesm/Articulos-Benchmarking-YOLOv8-to-YOLOv11}
}
```

