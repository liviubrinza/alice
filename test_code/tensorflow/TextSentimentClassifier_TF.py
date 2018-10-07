import tensorflow as tf
from tensorflow import keras

import numpy as np

# testing this training
# https://www.youtube.com/watch?v=BO4g2DRvL6U&index=3&list=PLQY2H8rRoyvwLbzbnKJ59NkZvQAW9wLbx

# download the imdb movie dataset
imdb = keras.datasets.imdb
(train_data, train_labels), (test_data, test_labels) = imdb.load_data(num_words=10000)

print("Training entries: {}, labels: {}".format(len(train_data), len(train_labels)))

# check the data format
print(train_data[0])

# A dictionary mapping words to an integer index
word_index = imdb.get_word_index()

# The first indices are reserved
word_index = {k:(v+3) for k,v in word_index.items()}
word_index["<PAD>"] = 0
word_index["<START>"] = 1
word_index["<UNK>"] = 2
word_index["<UNUSED>"] = 3

reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])


def decode_review(text):
    return ' '.join([reverse_word_index.get(i, "?") for i in text])

print(decode_review(train_data[0]))

print("First training data size: {}, second size: {}".format(len(train_data[0]), len(train_data[1])))

train_data = keras.preprocessing.sequence.pad_sequences(train_data,
                                                        value=word_index["<PAD>"],
                                                        padding='post',
                                                        maxlen=256)

test_data = keras.preprocessing.sequence.pad_sequences(test_data,
                                                       value=word_index["<PAD>"],
                                                       padding='post',
                                                       maxlen=256)
print("After padding:")
print("First training data size: {}, second size: {}".format(len(train_data[0]), len(train_data[1])))

# print the padded training data
print(train_data[0])


# do the actual words to vectors embedding
vocab_size = 10000

model = keras.Sequential()
model.add(keras.layers.Embedding(vocab_size, 16))
model.add(keras.layers.GlobalAveragePooling1D())
model.add(keras.layers.Dense(16, activation=tf.nn.relu))
model.add(keras.layers.Dense(1, activation=tf.nn.sigmoid))

model.summary()

model.compile(optimizer=tf.train.AdamOptimizer(), loss='binary_crossentropy', metrics=['accuracy'])

# split the training data: first 10.000 used for training, the rest for validation
x_val = train_data[:10000]
partial_x_train = train_data[10000:]

y_val = train_labels[:10000]
partial_y_train = train_labels[10000:]

# actually train the model
history = model.fit(partial_x_train,
                    partial_y_train,
                    epochs=40,
                    batch_size=512,
                    validation_data=(x_val, y_val),
                    verbose=1)

# evaluate the trained model
results = model.evaluate(test_data, test_labels)
print(results)

# test the model against a randomly generated review and one consisting only of the word brilliant (code 530)
rand_review = np.random.randint(10000, size=256)
biased_review = np.full(256, 530)
test_data = np.append(test_data, [rand_review], axis=0)
test_data = np.append(test_data, [biased_review], axis=0)

# now actually do the predictions
print(model.predict(test_data))
print(decode_review(test_data[-2]))
print(decode_review(test_data[-1]))


print("done")
