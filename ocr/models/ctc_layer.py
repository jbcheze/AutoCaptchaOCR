import tensorflow as tf
from keras import layers
from .vocab import num_chars

class CTCLayer(layers.Layer):
    def call(self, y_true, y_pred):
        batch = tf.shape(y_true)[0]
        input_len = tf.fill([batch], tf.shape(y_pred)[1])
        label_len = tf.reduce_sum(tf.cast(y_true >= 0, tf.int32), axis=1)

        sparse = tf.keras.backend.ctc_label_dense_to_sparse(y_true, label_len)

        loss = tf.nn.ctc_loss(
            labels=sparse,
            logits=tf.math.log(tf.transpose(y_pred, [1,0,2]) + 1e-8),
            label_length=label_len,
            logit_length=input_len,
            blank_index=num_chars,
        )

        self.add_loss(tf.reduce_mean(loss))
        return y_pred
