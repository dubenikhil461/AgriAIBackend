import os
import random
import shutil
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing import image

# ---------------- Dataset Split ----------------
def create_splits(src_root, dest_root, val_frac=0.15, test_frac=0.1, seed=42):
    random.seed(seed)
    os.makedirs(dest_root, exist_ok=True)
    classes = [d for d in os.listdir(src_root) if os.path.isdir(os.path.join(src_root, d))]
    for cls in classes:
        src_dir = os.path.join(src_root, cls)
        files = [os.path.join(src_dir, f) for f in os.listdir(src_dir)
                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        train_val, test = train_test_split(files, test_size=test_frac, random_state=seed, stratify=[cls]*len(files))
        train, val = train_test_split(train_val, test_size=val_frac/(1-test_frac), random_state=seed, stratify=[cls]*len(train_val))
        for split_name, split_files in [('train', train), ('val', val), ('test', test)]:
            out_dir = os.path.join(dest_root, split_name, cls)
            os.makedirs(out_dir, exist_ok=True)
            for f in split_files:
                shutil.copy(f, out_dir)

# ---------------- Preprocessing ----------------
def preprocess_image(img_bytes, img_size=224):
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    img = img.resize((img_size, img_size))
    img_arr = np.array(img)/255.0
    return np.expand_dims(img_arr, axis=0)
