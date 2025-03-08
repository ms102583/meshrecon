import os
import sys
import shutil

def main():
    if len(sys.argv) != 3:
        print("Usage: python merge.py <base_folder_name> <number_of_folders>")
        sys.exit(1)

    base_folder = sys.argv[1]
    try:
        num_folders = int(sys.argv[2])
    except ValueError:
        print("Error: <number_of_folders> must be an integer.")
        sys.exit(1)

    dest_folder = f"/home/minseong/Downloads/object_mask/{base_folder}"
    os.makedirs(dest_folder, exist_ok=True)

    for i in range(1, num_folders + 1):
        source_folder = f"/home/minseong/Downloads/object/{base_folder}{i}_mask"
        if not os.path.exists(source_folder):
            print(f"Warning: Source folder {source_folder} does not exist. Skipping.")
            continue
        for file_name in os.listdir(source_folder):
            source_file = os.path.join(source_folder, file_name)
            new_file_name = f"{i}_{file_name}"
            dest_file = os.path.join(dest_folder, new_file_name)
            try:
                shutil.copy2(source_file, dest_file)
                print(f"Moved: {source_file} -> {dest_file}")
            except Exception as e:
                print(f"Error moving {source_file}: {e}")

if __name__ == "__main__":
    main()
