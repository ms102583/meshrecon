import subprocess
import os
import shutil
import argparse

def run_colmap_pipeline(object_name):
    database_path = f"./mesh_colmap/{object_name}/database.db"
    image_path = f"./object/{object_name}_mask"
    input_path = f"./mesh_colmap/txt"
    sparse_model_path = f"./mesh_colmap/{object_name}/sparse"
    mesh_colmap_images = f"./mesh_colmap/{object_name}/images"

    os.makedirs(sparse_model_path, exist_ok=True)
    os.makedirs(mesh_colmap_images, exist_ok=True)
    
    for file in os.listdir(image_path):
        src_file = os.path.join(image_path, file)
        dst_file = os.path.join(mesh_colmap_images, file)
        shutil.copy2(src_file, dst_file)
    
    commands = [
        ["colmap", "feature_extractor", "--database_path", database_path, "--image_path", image_path, "--ImageReader.camera_model", "SIMPLE_PINHOLE", "--SiftExtraction.peak_threshold", "0.001", "--SiftExtraction.max_num_features", "20000"],
        ["colmap", "exhaustive_matcher", "--database_path", database_path],
        ["colmap", "mapper", "--database_path", database_path, "--image_path", image_path, "--output_path", sparse_model_path]
    ]
    
    for command in commands:
        subprocess.run(command, check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run COLMAP pipeline for a given object.")
    parser.add_argument("object_name", type=str, help="Name of the object to process")
    args = parser.parse_args()
    
    run_colmap_pipeline(args.object_name)
