# Just disables the warning, doesn't enable AVX/FMA
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# https://www.youtube.com/watch?v=BhpvH5DuVu8&index=46&list=PLQVvvaa0QuDfKTOs3Keq_kaG2P55YRn5v

'''
1. - input -> weight -> hidden layer 1 (activation function) -> weights -> hidden layer 2 (activation function)
 -> weights -> output layer
 
2. - compare output to intended output (cost / loss function) (cross entropy)
 
3. - optimization function (optimizer) > minimize cost (adam optimizer, SGD, AdaGrad ...)

4. - backpropagation

feed forward + backprop = EPOCH
'''

import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

tf.logging.set_verbosity(tf.logging.ERROR)

mnist = input_data.read_data_sets("/tmp/data", one_hot=True)

# 10 classes, 0-9
'''
    one hot encoding: 0 = [1,0,0,0,0,0,0,0,0,0]
'''

n_nodes_hl1 = 500
n_nodes_hl2 = 500
n_nodes_hl3 = 500

n_classes = 10

batch_size = 100

x = tf.placeholder('float', [None, 784])
y = tf.placeholder('float')

def neural_network_model(data):

    hidden_1_layer = {'weights': tf.Variable(tf.random_normal([784, n_nodes_hl1])),
                      'biases': tf.Variable(tf.random_normal([n_nodes_hl1]))}

    hidden_2_layer = {'weights': tf.Variable(tf.random_normal([n_nodes_hl1, n_nodes_hl2])),
                      'biases': tf.Variable(tf.random_normal([n_nodes_hl2]))}

    hidden_3_layer = {'weights': tf.Variable(tf.random_normal([n_nodes_hl2, n_nodes_hl3])),
                      'biases': tf.Variable(tf.random_normal([n_nodes_hl3]))}

    output_layer = {'weights': tf.Variable(tf.random_normal([n_nodes_hl3, n_classes])),
                    'biases': tf.Variable(tf.random_normal([n_classes]))}

    # (input_data * weights) + biases

    l1 = tf.add(tf.matmul(data, hidden_1_layer['weights']), hidden_1_layer['biases'])
    l1 = tf.nn.relu(l1)

    l2 = tf.add(tf.matmul(l1, hidden_2_layer['weights']), hidden_2_layer['biases'])
    l2 = tf.nn.relu(l2)

    l3 = tf.add(tf.matmul(l2, hidden_3_layer['weights']), hidden_3_layer['biases'])
    l3 = tf.nn.relu(l3)

    output = tf.matmul(l3, output_layer['weights']) + output_layer['biases']

    return output

# https://www.youtube.com/watch?v=PwAGxqrXSCs&list=PLQVvvaa0QuDfKTOs3Keq_kaG2P55YRn5v&index=47
def train_neural_network(x):
    global y
    prediction = neural_network_model(x)
    # define our cost function to use softmax variant (compare prediction with y)
    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=prediction, labels=y))
    # use the adam optimizer in order to minimize our cost
    optimizer = tf.train.AdamOptimizer().minimize(cost) # -> 95.14%
    # optimizer = tf.train.AdagradOptimizer(learning_rate=0.001).minimize(cost) -> 82.83%

    # number of feed forward + backprops
    hm_epochs = 10

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        for epoch in range(hm_epochs):
            epoch_loss = 0
            for _ in range(int(mnist.train.num_examples/batch_size)):
                epoch_x, epoch_y = mnist.train.next_batch(batch_size)
                _, c = sess.run([optimizer, cost], feed_dict={x: epoch_x, y: epoch_y})
                epoch_loss += c
            print("Epoch ", epoch, " completed out of ", hm_epochs, " loss", epoch_loss)

        correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(y, 1))
        accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
        print('Accuracy: ', accuracy.eval({x: mnist.test.images, y: mnist.test.labels}))

train_neural_network(x)

"""
    Using the mnist data set, this created a neural network that trained over the input and spat a 
    final accuracy of 0.95 over 10 epochs 
"""