from PIL import Image
import os

INPUT_DIR = '/Users/kbgreenberg/Downloads/OneDrive_1_5-12-2025/'
OUTPUT_DIR = '/Users/kbgreenberg/Downloads/OneDrive_1_5-12-2025/processed/'
TARGET_SIZE = (300, 300)

os.makedirs(OUTPUT_DIR, exist_ok=True)

for fname in os.listdir(INPUT_DIR):
    if not fname.lower().endswith(('.jpg', '.jpeg', '.png')):
        continue

    img = Image.open(os.path.join(INPUT_DIR, fname))
    w, h = img.size
    # center-crop to square of side = min(w,h)
    # side = min(w, h)
    # left   = (w - side) // 2
    # top    = (h - side) // 2
    # right  = left + side
    # bottom = top + side
    # cropped = img.crop((left, top, right, bottom))

    # resize down/up to target
    resized = img.resize(TARGET_SIZE, Image.LANCZOS)
    resized.save(os.path.join(OUTPUT_DIR, fname))