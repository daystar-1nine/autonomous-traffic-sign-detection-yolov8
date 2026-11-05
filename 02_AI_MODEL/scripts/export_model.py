"""
Model Export and Mobile Conversion Script
Autonomous AI Car Project
Supports: ONNX, TFLite (FP32/FP16), NCNN
"""

import argparse
import sys
from pathlib import Path
from ultralytics import YOLO

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))


def parse_args():
    parser = argparse.ArgumentParser(description="Export YOLO Model to Mobile / Edge Formats")
    parser.add_argument("--model", type=str, default="02_AI_MODEL/weights/best_yolov8n.pt", help="Path to .pt weights")
    parser.add_argument("--format", type=str, default="onnx", choices=["onnx", "tflite", "ncnn", "openvino"], help="Target format")
    parser.add_argument("--imgsz", type=int, default=640, help="Image resolution (640)")
    parser.add_argument("--half", action="store_true", help="FP16 half-precision quantization")
    parser.add_argument("--int8", action="store_true", help="INT8 quantization")
    parser.add_argument("--output-dir", type=str, default="02_AI_MODEL/exports", help="Export destination")
    return parser.parse_args()


def export():
    args = parse_args()
    model_path = Path(args.model)
    if not model_path.is_file():
        raise FileNotFoundError(f"Model not found at: {model_path.resolve()}")

    print(f"\n[INFO] Starting export for: {model_path.name}")
    print(f"Target Format : {args.format.upper()}")
    print(f"Resolution    : {args.imgsz}x{args.imgsz}")
    print(f"FP16 Half     : {args.half}")
    print(f"INT8 Quant    : {args.int8}")

    model = YOLO(str(model_path))

    export_kwargs = {
        "format": args.format,
        "imgsz": args.imgsz,
        "half": args.half,
        "int8": args.int8,
    }

    if args.format == "onnx":
        export_kwargs["opset"] = 18
        export_kwargs["simplify"] = False

    try:
        exported_path = model.export(**export_kwargs)
        print(f"\n[SUCCESS] Model exported successfully to: {exported_path}")

        # Verification for ONNX
        if args.format == "onnx":
            import onnx
            onnx_model = onnx.load(str(exported_path))
            onnx.checker.check_model(onnx_model)
            print("[VERIFIED] ONNX graph verified valid by onnx.checker!")
            for inp in onnx_model.graph.input:
                shape = [dim.dim_value or dim.dim_param for dim in inp.type.tensor_type.shape.dim]
                print(f" - Graph Input:  {inp.name} | Shape: {shape}")
            for out in onnx_model.graph.output:
                shape = [dim.dim_value or dim.dim_param for dim in out.type.tensor_type.shape.dim]
                print(f" - Graph Output: {out.name} | Shape: {shape}")

        return exported_path
    except Exception as e:
        print(f"\n[ERROR] Export failed: {e}")
        raise


if __name__ == "__main__":
    export()
