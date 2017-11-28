import numpy as np
import matplotlib.pyplot as plt

inputX = np.array([[0, 0, 1], [0, 1, 1], [1, 0, 1], [1, 1, 1]]) # (4,3)

outputY = np.array([[0, 0, 1, 1]]).T #(4,1)

# plt.matshow(np.hstack((X,y)), fignum=10, cmap=plt.cm.gray)
# plt.show()


#sigmoid function
def nonlin(x, derive=False):
    if derive==True:
        return x*(1-x)
    return 1/(1+np.exp(-x))


Xaxis = np.arange(-10, 10, 0.2)
#plt.plot(Xaxis, nonlin(Xaxis))
#plt.show()

np.random.seed(1)

# initialize weights for syn0
syn0 = 2*np.random.random((3,1)) -1

for iterations in range(15000):
    # forward propagation
    l0 = inputX
    l1 = nonlin(np.dot(l0, syn0))

    # how bad did we do
    l1_error = outputY - l1

    # multiply how much we missed by slope of the sigmoid
    l1_delta = l1_error * nonlin(l1, True)

    # update the weights
    syn0 += np.dot(l0.T, l1_delta)


print("Output: ")
print(l1)