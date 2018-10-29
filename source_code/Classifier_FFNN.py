import random

import tensorflow as tf
from OneHotEncoder import OneHotEncoder

encoder = OneHotEncoder()

encoder.load_training_corpus()
trainingCorpus = encoder.training_corpus_list
random.shuffle(trainingCorpus)

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

# placeholders for input and output data
# x is a placeholder defining the input data shape matrix of None X size (matrix height X matrix width)
x = tf.placeholder('float', [None, input_layer_size])
# y is a placeholder defining the output data shape (which is just a float label)
y = tf.placeholder('float')

def neural_network_model(data):
    hidden_1_layer = {'weights': tf.Variable(tf.random_normal([input_layer_size, n_nodes_hl1])),
                      'biases': tf.Variable(tf.random_normal([n_nodes_hl1]))}

    hidden_2_layer = {'weights': tf.Variable(tf.random_normal([n_nodes_hl1, n_nodes_hl2])),
                      'biases': tf.Variable(tf.random_normal([n_nodes_hl2]))}

    hidden_3_layer = {'weights': tf.Variable(tf.random_normal([n_nodes_hl2, n_nodes_hl3])),
                      'biases': tf.Variable(tf.random_normal([n_nodes_hl3]))}

    output_layer = {'weights': tf.Variable(tf.random_normal([n_nodes_hl3, output_layer_size])),
                    'biases': tf.Variable(tf.random_normal([output_layer_size]))}

    # (input_data * weights) + biases

    l1 = tf.add(tf.matmul(data, hidden_1_layer['weights']), hidden_1_layer['biases'])
    l1 = tf.nn.relu(l1)

    l2 = tf.add(tf.matmul(l1, hidden_2_layer['weights']), hidden_2_layer['biases'])
    l2 = tf.nn.relu(l2)

    l3 = tf.add(tf.matmul(l2, hidden_3_layer['weights']), hidden_3_layer['biases'])
    l3 = tf.nn.relu(l3)

    output = tf.matmul(l3, output_layer['weights']) + output_layer['biases']

    return output

def train_neural_network(x):
    global y
    prediction = neural_network_model(x)

    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=prediction, labels=y))

    optimizer = tf.train.AdamOptimizer().minimize(cost)

    hm_epochs = 50

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        for epoch in range(hm_epochs):
            _, c = sess.run([optimizer, cost], feed_dict={x: train_x, y: train_y})
            print("Epoch ",epoch, " completed out of ",hm_epochs, " loss ",c)

        correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(y, 1))
        accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
        print('Accuracy: ', accuracy.eval({x: test_x, y: test_y}))

train_neural_network(x)


