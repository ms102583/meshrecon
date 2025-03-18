import cv2
import os
import sys

def extract_frames(video_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    saved_frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break  
        
        if frame_count % 3 == 0:
            frame_filename = os.path.join(output_folder, f"{saved_frame_count:05d}.png")
            cv2.imwrite(frame_filename, frame)
            saved_frame_count += 1
        
        frame_count += 1
    
    cap.release()
    print(f"{saved_frame_count} frames saved in {output_folder}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python temp.py pringles")
        sys.exit(1)
    
    prefix = sys.argv[1]  # "pringles"
    
    video_file = f"videos/{prefix}.mp4"
    output_dir = f"object/{prefix}"
    extract_frames(video_file, output_dir)