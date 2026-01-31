import numpy as np
import tensorflow as tf
from .vocab import num_to_char

def decode_beam(preds, beam_width=10):
    input_len = np.ones(preds.shape[0]) * preds.shape[1]

    decoded, _ = tf.nn.ctc_beam_search_decoder(
        tf.math.log(tf.transpose(preds,[1,0,2]) + 1e-8),
        input_len.astype(np.int32),
        beam_width=beam_width,
    )

    dense = tf.sparse.to_dense(decoded[0], -1)

    texts = []
    for seq in dense:
        seq = seq[seq >= 0]
        texts.append(
            b"".join(tf.gather(num_to_char, seq).numpy()).decode()
        )
    return texts
