from NeuralNetwork import NeuralNetwork
from OneHotEncoder import OneHotEncoder

encoder = OneHotEncoder()
encoder.load_data()
net = NeuralNetwork(encoder)
# net.do_training()

while True:
    sentence = input("Enter command:")
    if sentence == "quit":
        break
    sentence = encoder.encode_sentence(sentence)
    print(encoder.categories[net.classify(sentence)])
