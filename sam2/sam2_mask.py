import os
import sys
import numpy as np
import torch
import shutil
from PIL import Image
from pathlib import Path

if len(sys.argv) != 2:
    print("Usage: python sam2_mask.py <folder_name>")
    sys.exit(1)
folder_name = sys.argv[1]

# 디렉토리 경로 설정
script_dir = Path(__file__).resolve().parent
parent_dir = script_dir.parent
object_dir = parent_dir / "object"
input_dir = str(object_dir / folder_name)  
converted_dir = str(object_dir / f"{folder_name}_jpg")  
output_dir = str(object_dir / f"{folder_name}_mask")  

os.makedirs(converted_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

png_files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith('.png')])
if not png_files:
    raise ValueError(f"No PNG files found in {input_dir}")

for file_name in png_files:
    input_path = os.path.join(input_dir, file_name)
    image = Image.open(input_path)
    if image.mode in ("RGBA", "LA"):
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        image = background
    else:
        image = image.convert("RGB")
    base_name = os.path.splitext(file_name)[0]
    output_file_name = base_name + ".jpg"
    output_path = os.path.join(converted_dir, output_file_name)
    image.save(output_path, "JPEG")

if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")

if device.type == "cuda":
    torch.autocast("cuda", dtype=torch.bfloat16).__enter__()
    if torch.cuda.get_device_properties(0).major >= 8:
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
elif device.type == "mps":
    print("MPS device support is experimental. SAM2 is trained with CUDA and might give different results.")

from sam2.build_sam import build_sam2_video_predictor

sam2_checkpoint = "./checkpoints/sam2.1_hiera_large.pt"
model_cfg = "configs/sam2.1/sam2.1_hiera_l.yaml"

predictor = build_sam2_video_predictor(model_cfg, sam2_checkpoint, device=device)

video_dir = converted_dir
frame_names = sorted([f for f in os.listdir(video_dir) if os.path.splitext(f)[-1].lower() in [".jpg", ".jpeg"]])
if not frame_names:
    raise ValueError(f"No JPG files found in {video_dir}")

inference_state = predictor.init_state(video_path=video_dir)
predictor.reset_state(inference_state)

ann_frame_idx = 0
ann_obj_id = 1
points = np.array([[1000, 600]], dtype=np.float32)
labels = np.array([1], dtype=np.int32)

_, out_obj_ids, out_mask_logits = predictor.add_new_points_or_box(
    inference_state=inference_state,
    frame_idx=ann_frame_idx,
    obj_id=ann_obj_id,
    points=points,
    labels=labels,
)

video_segments = {}  # key: frame index, value: {obj_id: mask}
for out_frame_idx, out_obj_ids, out_mask_logits in predictor.propagate_in_video(inference_state):
    video_segments[out_frame_idx] = {
        out_obj_id: (out_mask_logits[i] > 0.0).cpu().numpy()
        for i, out_obj_id in enumerate(out_obj_ids)
    }

for idx, file_name in enumerate(frame_names):
    if idx not in video_segments:
        print(f"No segmentation result for frame index {idx}")
        continue
    masks = video_segments[idx]
    if not masks:
        print(f"No mask found for frame index {idx}")
        continue
    selected_mask = list(masks.values())[0]
    if selected_mask.ndim == 3 and selected_mask.shape[0] == 1:
        selected_mask = selected_mask[0]
    alpha = (selected_mask * 255).astype('uint8')
    
    orig_file_name = png_files[idx]
    orig_img_path = os.path.join(input_dir, orig_file_name)
    orig_img = Image.open(orig_img_path).convert("RGB")
    
    orig_img.putalpha(Image.fromarray(alpha))
    
    save_path = os.path.join(output_dir, orig_file_name)
    orig_img.save(save_path, "PNG")
print(f"Saved RGBA image")

try:
    shutil.rmtree(converted_dir)
except Exception as e:
    print(f"Error deleting folder {converted_dir}: {e}")