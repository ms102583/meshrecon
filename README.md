# meshrecon

## 🛠 Environment Setup

To set up the required environments, run the following commands:

### **1️⃣ Install 2D Gaussian Splatting environment**
```bash
conda env create --file 2d-gaussian-splatting/environment.yml
```
🔗 [2D Gaussian Splatting Repository](https://github.com/hbb1/2d-gaussian-splatting)

### **2️⃣ Install SAM2 environment**
```bash
conda env create --file sam2/environment.yml
```
🔗 [SAM2 Repository](https://github.com/facebookresearch/sam2)

---

## 🚀 Usage

### **1️⃣ Place your video file in the `videos/` directory**
For example:
```
videos/pringles_tape.mp4
```

### **2️⃣ Run the pipeline script**
```bash
./pipeline.sh {object_name}
```
Example:
```bash
./pipeline.sh pringles_tape
```

---

## ⚠️ Important Notes

- **Example video resolution**: `1080x1920`  
  → The **initial point for SAM2** is set in `sam2/sam2_mask.py` at **line 75**:
  ```python
  points = np.array([[1000, 600]], dtype=np.float32)
  ```
  If your video has a different resolution, you may need to adjust this value.

---

## 📌 Repository Structure
```
meshrecon/
️│── 2d-gaussian-splatting/
️│── sam2/
️│── videos/            # Place your input videos here
️│── object/            # Extracted frames will be saved here
️│── mesh_colmap/       # COLMAP output will be stored here
️│── pipeline.sh        # Main pipeline script
️│── colmap.py          # COLMAP processing script
️│── README.md          # This file
```


