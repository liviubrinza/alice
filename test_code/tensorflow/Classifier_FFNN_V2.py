import random

import numpy as np
import tensorflow as tf
from OneHotEncoder import OneHotEncoder

# https://www.youtube.com/watch?v=yX8KuPZCAMo

encoder = OneHotEncoder()

encoder.load_data()
trainingCorpus = encoder.training_corpus_list

random.shuffle(trainingCorpus)

# test data size = 10% * training coprus
testing_size = int(0.1 * len(trainingCorpus))

training_set = trainingCorpus[:-testing_size]
testing_set = trainingCorpus[-testing_size:]

train_x = list(x[0] for x in training_set)
train_y = list(x[1] for x in training_set)

test_x = list(x[0] for x in testing_set)
test_y = list(x[1] for x in testing_set)

input_layer_size = len(train_x[0])
output_layer_size = len(train_y[0])

n_nodes_hl1 = 500
n_nodes_hl2 = 500
n_nodes_hl3 = 500

learning_rate = 0.03
training_epochs = 100
cost_history = np.empty(shape=[1], dtype=float)

model_path = "/mnt/28385DB3385D812C/GitBase/alice/source_code/trained_model/"

x = tf.placeholder(tf.float32, [None, input_layer_size])
y_ = tf.placeholder(tf.float32, [None, output_layer_size])

def multilayer_perceptron(x, weights, biases):

    layer_1 = tf.add(tf.matmul(x, weights["h1"]), biases["b1"])
    layer_1 = tf.nn.sigmoid(layer_1)

    layer_2 = tf.add(tf.matmul(layer_1, weights["h2"]), biases["b2"])
    layer_2 = tf.nn.sigmoid(layer_2)

    layer_3 = tf.add(tf.matmul(layer_2, weights["h3"]), biases["b3"])
    layer_3 = tf.nn.relu(layer_3)

    out_layer = tf.matmul(layer_3, weights["out"]) + biases["out"]
    return out_layer

weights = {
    "h1": tf.Variable(tf.truncated_normal([input_layer_size, n_nodes_hl1])),
    "h2": tf.Variable(tf.truncated_normal([n_nodes_hl1, n_nodes_hl2])),
    "h3": tf.Variable(tf.truncated_normal([n_nodes_hl2, n_nodes_hl3])),
    "out": tf.Variable(tf.truncated_normal([n_nodes_hl3, output_layer_size]))
}

biases = {
    "b1": tf.Variable(tf.truncated_normal([n_nodes_hl1])),
    "b2": tf.Variable(tf.truncated_normal([n_nodes_hl2])),
    "b3": tf.Variable(tf.truncated_normal([n_nodes_hl3])),
    "out": tf.Variable(tf.truncated_normal([output_layer_size])),
}

init = tf.global_variables_initializer()

saver = tf.train.Saver()

y = multilayer_perceptron(x, weights, biases)

cost_function = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=y, labels=y_))
training_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost_function)

sess = tf.Session()
sess.run(init)

mse_history = []
accuracy_history = []

for epoch in range(training_epochs):
    sess.run(training_step, feed_dict={x: train_x, y_:train_y})
    cost = sess.run(cost_function, feed_dict={x: train_x, y_: train_y})
    cost_history = np.append(cost_history, cost)
    correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    pred_y = sess.run(y, feed_dict={x: test_x})
    mse = tf.reduce_mean(tf.square(pred_y - test_y))
    mse_ = sess.run(mse)
    mse_history.append(mse)
    accuracy = (sess.run(accuracy, feed_dict={x: train_x, y_:train_y}))
    accuracy_history.append(accuracy)

    print("epoch: ", epoch, " - ", "cost", cost, " - MSE: ", mse_, " - train accuracy: ", accuracy)

save_path = saver.save(sess, model_path)
print("Model saved in file: %s", save_path)

# plt.plot(mse_history, 'r')
# plt.show()
# plt.plot(accuracy_history)
# plt.show()

correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
print("Test accuracy: ", (sess.run(accuracy, feed_dict={x: test_x, y_: test_y})))

pred_y = sess.run(y, feed_dict={x: test_x})
mse = tf.reduce_mean(tf.square(pred_y - test_y))
print("MSE: %.4f" % sess.run(mse))

# now let's restore the model
init = tf.global_variables_initializer()
saver = tf.train.Saver()
sess = tf.Session()
sess.run(init)
saver.restore(sess, model_path)

prediction = tf.argmax(y, 1)
correct_prediction = tf.equal(prediction, tf.argmax(y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

prediction_run = sess.run(prediction, feed_dict={x: train_x[10].reshape(1, input_layer_size)})
accuracy_run = sess.run(accuracy, feed_dict={x: train_x[10].reshape(1, input_layer_size), y_: train_y[10].reshape(1, output_layer_size)})
print("Original class: ", train_y[10], " predicted: ", prediction_run)
