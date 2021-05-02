###############################################################################
# Import Tensorflow and other libraries
###############################################################################
import tensorflow as tf
from tensorflow.keras.layers.experimental import preprocessing
import numpy as np
import os
import time
import sys

###############################################################################
# Constants
###############################################################################
# do not change the desired output variables here, change it in the OneStep model
vocab = ['\n', ' ', '!', '$', '&', "'", ',', '-', '.', '3', ':', ';', '?', 'A', 'B', 'C', 'D', 'E', 'F',
         'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
# preprocessing.StringLookup layer
ids_from_chars = preprocessing.StringLookup(vocabulary=list(vocab))
chars_from_ids = tf.keras.layers.experimental.preprocessing.StringLookup(vocabulary=ids_from_chars.get_vocabulary(),
                                                                         invert=True)

###############################################################################
# Modeling
###############################################################################
# Length of the vocabulary in chars
vocab_size = len(vocab)
# The embedding dimension
embedding_dim = 256
# Number of RNN units
rnn_units = 1024


class MyModel(tf.keras.Model):
    def __init__(self, vocab_size, embedding_dim, rnn_units):
        super().__init__(self)
        self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)
        self.gru = tf.keras.layers.GRU(rnn_units, return_sequences=True, return_state=True)
        self.dense = tf.keras.layers.Dense(vocab_size)

    def call(self, inputs, states=None, return_state=False, training=False):
        x = inputs
        x = self.embedding(x, training=training)
        if states is None:
            states = self.gru.get_initial_state(x)
        x, states = self.gru(x, initial_state=states, training=training)
        x = self.dense(x, training=training)
        if return_state:
            return x, states
        else:
            return x


model = MyModel(
    # Be sure the vocabulary size matches the 'StringLookup' layers.
    vocab_size=len(ids_from_chars.get_vocabulary()),
    embedding_dim=embedding_dim,
    rnn_units=rnn_units
)


class OneStep(tf.keras.Model):
    def __init__(self, model, chars_from_ids, ids_from_chars, temperature=1.0):
        super().__init__()
        self.temperature = temperature
        self.model = model
        self.chars_from_ids = chars_from_ids
        self.ids_from_chars = ids_from_chars
        # Create a mask to prevent "" or "[UNK]", and other unwanted chars from being generated.
        skip_ids = ['', '[UNK]', '\n', '-', ':']
        indices = np.array(list(range(0, len(skip_ids))))
        indices = indices[:, None]
        skip_ids = tf.sparse.SparseTensor(indices=indices, values=skip_ids, dense_shape=[len(skip_ids)])
        skip_ids = self.ids_from_chars(tf.sparse.reorder(skip_ids).values[:, None])
        sparse_mask = tf.SparseTensor(
            # Put a -inf at each bad index.
            values=[-float('inf')] * len(skip_ids),
            indices=skip_ids,
            # Match the shape to the vocabulary
            dense_shape=[len(ids_from_chars.get_vocabulary())])
        self.prediction_mask = tf.sparse.to_dense(sparse_mask)

    @tf.function
    def generate_one_step(self, inputs, states=None):
        # Convert strings to token IDs.
        input_chars = tf.strings.unicode_split(inputs, 'UTF-8')
        input_ids = self.ids_from_chars(input_chars).to_tensor()

        # Run the model.
        # predicted_logits.shape is [batch, char, next_char_logits]
        predicted_logits, states = self.model(inputs=input_ids, states=states,
                                              return_state=True)
        # Only use the last prediction.
        predicted_logits = predicted_logits[:, -1, :]
        predicted_logits = predicted_logits / self.temperature

        # Apply the prediction mask: prevent "" or "[UNK]" from being generated.
        predicted_logits = predicted_logits + self.prediction_mask

        # Sample the output logits to generate token IDs.
        prob_dist = tf.squeeze(tf.nn.softmax(predicted_logits))

        # 5 most likely predicted chars
        indices = tf.argsort(predicted_logits, axis=-1)[0][-5:][::-1]

        # their respective probs
        max_probs = tf.gather(prob_dist, indices=indices)
        max_chars = self.chars_from_ids(indices)

        # Return the characters and model state.
        return max_chars, states


def get_one_step_model():
    one_step_model = OneStep(model, chars_from_ids, ids_from_chars, temperature=0.6)
    # assume the main file is run at the outermost directory, and text-generation dir is parallel to the main file
    textgen_path = [dir for dir in sys.path if os.path.split(dir)[1] == 'text generation'][0]
    textgen_path = os.path.join(textgen_path, "one_step")
    one_step_model.load_weights(textgen_path)
    return one_step_model


print("textgen initialization success")
# ------------------------ Demo on how the model should be used --------------------------
# states = None
# next_char = [input("Pick a character: ")]
# result = [next_char]
# print("current sentence:", result[0][0])
# print()
# for n in range(20):
#     next_chars, states = one_step_model.generate_one_step(next_char, states=states)
#     next_chars = [x.decode('utf-8') for x in next_chars.numpy()]
#     print(next_chars)
#     next_char = [input("Pick a character: ")]
#     result.append(next_char)
#     print("current sentence:", tf.strings.join(result)[0].numpy().decode('utf-8'))
#     print()
#
# result = tf.strings.join(result)
# print("\nsentence:", result[0].numpy().decode('utf-8'), '\n\n' + '_' * 80)
# print('\nRun time:', end - start)
# tf.print(result)
