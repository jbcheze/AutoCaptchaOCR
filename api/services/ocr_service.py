import numpy as np
import tensorflow as tf
from keras.models import load_model
from keras import layers
from pathlib import Path


# ======================
# CONFIG (IDENTIQUE NOTEBOOK)
# ======================
IMG_WIDTH, IMG_HEIGHT = 200, 50
CHARS = "0123456789abcdefghijklmnopqrstuvwxyz"
NUM_CHARS = len(CHARS)


class OCRService:
    """
    OCR Service strictement identique au notebook de test.
    Garantit des performances équivalentes.
    """

    def __init__(self, model_path: str):
        # Charger le modèle d'inférence (SANS CTCLayer)
        self.infer_model = load_model(model_path, compile=False)

        # Decoder vocab (IDENTIQUE)
        self.num_to_char = layers.StringLookup(
            vocabulary=list(CHARS),
            mask_token=None,
            invert=True
        )

    # ======================
    # IMAGE LOADER (COPIE NOTEBOOK)
    # ======================
    def _load_image(self, path: str):
        img = tf.io.decode_image(
            tf.io.read_file(path),
            channels=1,
            expand_animations=False
        )

        img = tf.image.resize(
            tf.image.convert_image_dtype(img, tf.float32),
            [IMG_HEIGHT, IMG_WIDTH]
        )

        img = tf.transpose(img, [1, 0, 2])
        return img

    # ======================
    # PREDICT TEXT (COPIE NOTEBOOK)
    # ======================
    def predict(self, image_path: str) -> str:
        img = self._load_image(image_path)
        img = tf.expand_dims(img, 0)

        pred = self.infer_model(img, training=False)

        decoded, _ = tf.keras.backend.ctc_decode(
            pred,
            input_length=np.ones(pred.shape[0]) * pred.shape[1],
            greedy=True
        )

        seq = decoded[0][0].numpy()

        # garder uniquement caractères valides
        seq = seq[(seq >= 0) & (seq < NUM_CHARS)]

        # 🔥 FIX CRITIQUE : StringLookup invert attend index >= 1
        seq = seq + 1

        text = "".join(self.num_to_char(seq).numpy().astype(str))
        return text.lower()