import tensorflow as tf
from keras import layers

characters = list("0123456789abcdefghijklmnopqrstuvwxyz")
num_chars = len(characters)
num_classes = num_chars + 1

char_to_num = layers.StringLookup(
    vocabulary=characters,
    mask_token=None,
    num_oov_indices=0
)

num_to_char = tf.constant(characters)
