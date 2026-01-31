import keras
from keras import layers
from .ctc_layer import CTCLayer
from .vocab import num_classes

IMG_WIDTH = 200
IMG_HEIGHT = 50

def build_ocr_model():
    img = layers.Input((IMG_WIDTH, IMG_HEIGHT, 1), name="image")
    lbl = layers.Input((None,), dtype="int32", name="label")

    x = layers.Conv2D(64, 3, padding="same", activation="relu")(img)
    x = layers.MaxPooling2D((2,2))(x)

    x = layers.Conv2D(128, 3, padding="same", activation="relu")(x)
    x = layers.MaxPooling2D((2,1))(x)

    x = layers.Reshape((IMG_WIDTH//4, (IMG_HEIGHT//2)*128))(x)
    x = layers.Dense(128, activation="relu")(x)

    x = layers.Bidirectional(layers.LSTM(256, return_sequences=True))(x)
    x = layers.Bidirectional(layers.LSTM(128, return_sequences=True))(x)

    y = layers.Dense(num_classes, activation="softmax")(x)
    out = CTCLayer()(lbl, y)

    return keras.Model([img, lbl], out)
