# Just disables the warning, doesn't enable AVX/FMA
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import random
import numpy as np
import tensorflow as tf
from OneHotEncoder import OneHotEncoder
from FileHandler import FileHandler

# https://www.youtube.com/watch?v=yX8KuPZCAMo

class NeuralNetwork:

    def __init__(self, encoder):
        self.saver = None
        self.encoder = encoder
        self.model_path = "trained_model/"
        self.imprecision_threshold = 0.85

        self.train_x = None
        self.train_y = None

        self.test_x = None
        self.test_y = None

        self.input_layer_size = None
        self.output_layer_size = None

        self.load_training_data()

        self.n_nodes_hl1 = 500
        self.n_nodes_hl2 = 500
        self.n_nodes_hl3 = 500

        self.learning_rate = 0.01
        self.training_epochs = 100
        self.training_shuffle_iterations = 2
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

    def load_training_data(self):
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

        self.network_structure = self.multilayer_perceptron(self.x, self.weights, self.biases)

        cost_function = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=self.network_flow, labels=self.y_))
        optimizer = tf.train.GradientDescentOptimizer(self.learning_rate).minimize(cost_function)
        # optimizer = tf.train.AdamOptimizer().minimize(cost_function)
        # NOTE : THIS WAS THE WORST OF ALL
        #optimizer = tf.train.AdadeltaOptimizer().minimize(cost_function)
        #optimizer = tf.train.MomentumOptimizer(learning_rate=self.learning_rate, momentum=0.4).minimize(cost_function)
        #optimizer = tf.train.AdagradOptimizer(self.learning_rate).minimize(cost_function)

        init = tf.global_variables_initializer()

        sess = tf.Session()
        sess.run(init)

        mse_history = []
        accuracy_history = []

        for iteration in range(self.training_shuffle_iterations):
            self.load_training_data()

            for epoch in range(self.training_epochs):
                sess.run(optimizer, feed_dict={self.x: self.train_x, self.y_: self.train_y})
                cost = sess.run(cost_function, feed_dict={self.x: self.train_x, self.y_: self.train_y})
                self.cost_history = np.append(self.cost_history, cost)
                correct_prediction = tf.equal(tf.argmax(self.network_structure, 1), tf.argmax(self.y_, 1))
                accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
                pred_y = sess.run(self.network_structure, feed_dict={self.x: self.test_x})
                mse = tf.reduce_mean(tf.square(pred_y - self.test_y))
                mse_ = sess.run(mse)
                mse_history.append(mse)
                accuracy = (sess.run(accuracy, feed_dict={self.x: self.train_x, self.y_: self.train_y}))
                accuracy_history.append(accuracy)

                print("epoch: ", epoch, " - ", "cost", cost, " - MSE: ", mse_, " - train accuracy: ", accuracy)

        self.saver = tf.train.Saver()
        self.saver.save(sess, self.model_path)

    def get_prediction_percentages(self, numpy_array):
        clamped_values = list()
        normalized_values = list()

        values_list = numpy_array.tolist()[0]

        [clamped_values.append(round(value, 2)) for value in values_list]

        max_val = max(clamped_values)
        min_val = min(clamped_values)

        for value in clamped_values:
            normalized = (value - min_val) / (max_val - min_val)
            normalized_values.append(round(normalized, 2))

        return normalized_values

    def classify(self, command):
        values_pred_run = self.session.run(self.network_flow, feed_dict={self.x: command.reshape(1, self.input_layer_size)})
        #print("-> Bare predictions array: " + str(values_pred_run))

        guesses = self.get_prediction_percentages(values_pred_run)
        #print(guesses)

        for guess in guesses:
            if guess > self.imprecision_threshold and guess != 1.0:
                return -1, guesses

        return guesses.index(1.0), guesses

    def load(self):
        if not os.listdir(self.model_path):
            self.do_training()

        init = tf.global_variables_initializer()

        self.saver = tf.train.Saver()
        self.session = tf.Session()
        self.session.run(init)
        self.saver.restore(self.session, self.model_path)

    def get_training_corpus_list(self):
        file_handler = FileHandler()
        training_corpus = file_handler.read_training_corpus()

        entries_list = list()

        for entry in training_corpus:
            entry = entry.strip()
            if entry == "":
                continue
            entry_dict = {"class": entry.split(":")[0].strip(),
                          "sentence": entry.split(":")[1].strip()}
            entries_list.append(entry_dict)

        return entries_list

    def test_accuracy(self):
        test_list = self.get_training_corpus_list()

        entries_count = len(test_list)
        correct_guesses = 0
        incorrect_guesses = 0
        misclassified_sentences = list()

        for entry in test_list:
            encoded_sentence = self.encoder.encode_sentence(entry["sentence"])
            guess, guesses = self.classify(encoded_sentence)

            guess_category = self.encoder.categories[guess]

            if guess_category == entry["class"]:
                correct_guesses += 1
            else:
                incorrect_guesses += 1
                misclassified_sentences.append([entry["sentence"], guesses])

        print("Accuracy:", round(((correct_guesses * 100) / entries_count), 2))
        print("Total tested:", entries_count)
        print("Correct guesses:", correct_guesses)
        print("Incorrect guesses:", incorrect_guesses)
        print()
        print("Misclassified sentences:")

        for count in range(0, incorrect_guesses):
            print("%s. %s." % (count, misclassified_sentences[count][0]))
            print("\tGuessed: %s", misclassified_sentences[count][1])

if __name__ == '__main__':
    encoder = OneHotEncoder()
    encoder.load_data()
    net = NeuralNetwork(encoder)

    """ test accuracy """
    net.test_accuracy()
