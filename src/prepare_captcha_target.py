from pathlib import Path
import shutil
import random
from class_mapping import CHAR2ID

SOURCE = Path("data/my_600_captchas")
TARGET = Path("datasets/captcha_target")
TRAIN_RATIO = 0.85
IMG_EXT = [".png", ".jpg", ".jpeg"]

for split in ["train", "valid"]:
    (TARGET / split / "images").mkdir(parents=True, exist_ok=True)
    (TARGET / split / "labels").mkdir(parents=True, exist_ok=True)

images = [p for p in SOURCE.iterdir() if p.suffix.lower() in IMG_EXT]
random.shuffle(images)

split_idx = int(len(images) * TRAIN_RATIO)
splits = {
    "train": images[:split_idx],
    "valid": images[split_idx:]
}

for split, imgs in splits.items():
    for img_path in imgs:
        text = img_path.stem
        n = len(text)

        label_file = TARGET / split / "labels" / f"{img_path.stem}.txt"

        with open(label_file, "w") as f:
            for i, char in enumerate(text):
                if char not in CHAR2ID:
                    continue

                cls = CHAR2ID[char]
                x_center = (i + 0.5) / n
                y_center = 0.5
                width = 1.0 / n
                height = 0.8

                f.write(f"{cls} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

        shutil.copy(
            img_path,
            TARGET / split / "images" / img_path.name
        )

print("✅ Dataset captcha_target prêt")
