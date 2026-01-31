import tensorflow as tf

IMG_WIDTH = 200
IMG_HEIGHT = 50

def preprocess_image(img_path):
    img = tf.io.read_file(img_path)
    img = tf.io.decode_png(img, channels=1)
    img = tf.image.convert_image_dtype(img, tf.float32)
    img = tf.image.resize(img, [IMG_HEIGHT, IMG_WIDTH])
    img = tf.transpose(img, [1, 0, 2])
    return img
