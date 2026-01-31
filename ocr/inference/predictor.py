import numpy as np
import tensorflow as tf
import keras

from ocr.preprocess import preprocess_image
from ocr.decoder import decode_beam
from ocr.vocab import num_to_char
from ocr.ctc_layer import CTCLayer


class OCRPredictor:
    def __init__(self, model_path: str):
        # Charger le modèle entraîné
        self.model = keras.models.load_model(
            model_path,
            custom_objects={"CTCLayer": CTCLayer}
        )

        # Modèle de prédiction (sans la couche CTC)
        self.prediction_model = keras.Model(
            self.model.input[0],
            self.model.layers[-2].output
        )

    def predict(self, image_path: str) -> str:
        """
        Prédit le texte d'une image captcha
        """
        # 1) Preprocess image
        image = preprocess_image(image_path)
        image = tf.expand_dims(image, axis=0)  # batch = 1

        # 2) Prédiction réseau
        preds = self.prediction_model.predict(image, verbose=0)

        # 3) Décodage CTC (beam search)
        text = decode_beam(preds)[0]

        return text
