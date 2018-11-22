# Just disables the warning, doesn't enable AVX/FMA
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import random
import numpy as np
import tensorflow as tf
from OneHotEncoder import OneHotEncoder

# https://www.youtube.com/watch?v=yX8KuPZCAMo

class NeuralNetwork:

    def __init__(self, encoder):
        self.saver = None
        self.encoder = encoder
        self.model_path = "trained_model/"

        training_corpus = self.encoder.training_corpus_list

        random.shuffle(training_corpus)

        # test data size = 10% * training corpus
        testing_size = int(0.1 * len(training_corpus))

        training_set = training_corpus[:-testing_size]
        testing_set = training_corpus[-testing_size:]

        self.train_x = list(x[0] for x in training_set)
        self.train_y = list(x[1] for x in training_set)

        self.test_x = list(x[0] for x in testing_set)
        self.test_y = list(x[1] for x in testing_set)

        self.input_layer_size = len(self.train_x[0])
        self.output_layer_size = len(self.train_y[0])

        self.n_nodes_hl1 = 500
        self.n_nodes_hl2 = 500
        self.n_nodes_hl3 = 500

        self.learning_rate = 0.03
        self.training_epochs = 100
        self.cost_history = np.empty(shape=[1], dtype=float)

        self.x = tf.placeholder(tf.float32, [None, self.input_layer_size])
        self.y_ = tf.placeholder(tf.float32, [None, self.output_layer_size])

        self.session = tf.Session()

        self.weights = {
            "h1": tf.Variable(tf.truncated_normal([self.input_layer_size, self.n_nodes_hl1])),
            "h2": tf.Variable(tf.truncated_normal([self.n_nodes_hl1, self.n_nodes_hl2])),
            "h3": tf.Variable(tf.truncated_normal([self.n_nodes_hl2, self.n_nodes_hl3])),
            "out": tf.Variable(tf.truncated_normal([self.n_nodes_hl3, self.output_layer_size]))
        }

        self.biases = {
            "b1": tf.Variable(tf.truncated_normal([self.n_nodes_hl1])),
            "b2": tf.Variable(tf.truncated_normal([self.n_nodes_hl2])),
            "b3": tf.Variable(tf.truncated_normal([self.n_nodes_hl3])),
            "out": tf.Variable(tf.truncated_normal([self.output_layer_size])),
        }
        self.network_flow = self.multilayer_perceptron(self.x, self.weights, self.biases)

        self.load()

    def multilayer_perceptron(self, x, weights, biases):
        layer_1 = tf.add(tf.matmul(x, weights["h1"]), biases["b1"])
        layer_1 = tf.nn.sigmoid(layer_1)

        layer_2 = tf.add(tf.matmul(layer_1, weights["h2"]), biases["b2"])
        layer_2 = tf.nn.sigmoid(layer_2)

        layer_3 = tf.add(tf.matmul(layer_2, weights["h3"]), biases["b3"])
        layer_3 = tf.nn.relu(layer_3)

        out_layer = tf.matmul(layer_3, weights["out"]) + biases["out"]
        return out_layer

    def do_training(self):
        init = tf.global_variables_initializer()
        # self.network_structure = self.multilayer_perceptron(self.x, self.weights, self.biases)

        cost_function = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=self.network_flow, labels=self.y_))
        optimizer = tf.train.GradientDescentOptimizer(self.learning_rate).minimize(cost_function)

        sess = tf.Session()
        sess.run(init)

        mse_history = []
        accuracy_history = []

        for epoch in range(self.training_epochs):
            sess.run(optimizer, feed_dict={self.x: self.train_x, self.y_: self.train_y})
            cost = sess.run(cost_function, feed_dict={self.x: self.train_x, self.y_: self.train_y})
            self.cost_history = np.append(self.cost_history, cost)
            correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(self.y_, 1))
            accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
            pred_y = sess.run(y, feed_dict={self.x: self.test_x})
            mse = tf.reduce_mean(tf.square(pred_y - self.test_y))
            mse_ = sess.run(mse)
            mse_history.append(mse)
            accuracy = (sess.run(accuracy, feed_dict={self.x: self.train_x, self.y_: self.train_y}))
            accuracy_history.append(accuracy)

            print("epoch: ", epoch, " - ", "cost", cost, " - MSE: ", mse_, " - train accuracy: ", accuracy)

        self.saver = tf.train.Saver()
        self.saver.save(sess, self.model_path)

    def classify(self, command):
        array_prediction = tf.nn.softmax(self.network_flow, 1)
        array_pred_run = self.session.run(array_prediction, feed_dict={self.x: command.reshape(1, self.input_layer_size)})

        class_prediction = tf.argmax(self.network_flow, 1)
        class_pred_run = self.session.run(class_prediction, feed_dict={self.x: command.reshape(1, self.input_layer_size)})

        # print("-> Predictions array: " + str(array_pred_run))
        # print("-> Prediction class: " + str(np.asscalar(class_pred_run)))
        return np.asscalar(class_pred_run)

    def load(self):
        init = tf.global_variables_initializer()

        self.saver = tf.train.Saver()
        self.session = tf.Session()
        self.session.run(init)
        self.saver.restore(self.session, self.model_path)

if __name__ == '__main__':
    encoder = OneHotEncoder()
    encoder.load_data()
    net = NeuralNetwork(encoder)
    # net.do_training()

    sentence = encoder.encode_sentence("Turn on the light")
    print(encoder.categories[net.classify(sentence)])
    sentence = encoder.encode_sentence("hello there")
    print(encoder.categories[net.classify(sentence)])
    sentence = encoder.encode_sentence("make it warmer")
    print(encoder.categories[net.classify(sentence)])
