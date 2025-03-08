#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <object_name>"
    exit 1
fi

OBJECT_NAME=$1
BASE_DIR=$(realpath "$(dirname "$0")")
OUTPUT_DIR="2d-gaussian-splatting/output"
MESH_COLMAP_DIR="$BASE_DIR/mesh_colmap/$OBJECT_NAME"

echo "Processing object: $OBJECT_NAME"

source ~/miniconda3/etc/profile.d/conda.sh

# 1. Extract frames
echo "Extracting frames..."
python extract_frames.py "$OBJECT_NAME"

# 2. Run SAM2 Mask
echo "Running SAM2 Mask..."
cd sam2
conda activate sam2
python sam2_mask.py "$OBJECT_NAME"
conda deactivate
cd -

# 3. Run COLMAP pipeline
echo "Running COLMAP pipeline..."
conda activate surfel_splatting
python colmap.py "$OBJECT_NAME"

# 4. Run Gaussian Splatting training
echo "Training Gaussian Splatting..."
cd 2d-gaussian-splatting
python train.py -s "$MESH_COLMAP_DIR"
cd -

echo "Waiting for training output directory..."
sleep 5  

NEW_MODEL_PATH=$(ls -td "$OUTPUT_DIR"/* | head -1)  

if [ -z "$NEW_MODEL_PATH" ]; then
    echo "Error: No new output directory found after training."
    exit 1
fi

touch "$NEW_MODEL_PATH/$OBJECT_NAME.txt"

echo "Rendering..."
python 2d-gaussian-splatting/render.py -m "$NEW_MODEL_PATH" -s "$MESH_COLMAP_DIR"
conda deactivate

echo "Pipeline completed"
