from NeuralNetwork import NeuralNetwork
from OneHotEncoder import OneHotEncoder

def get_value(sentence):
    words = sentence.split()
    for word in words:
        try:
            return int(word)
        except ValueError:
            continue
    return None

encoder = OneHotEncoder()
encoder.load_data()
net = NeuralNetwork(encoder)
# net.do_training()

while True:
    sentence = input("Enter command:")
    if sentence == "quit":
        break
    encoded_sentence = encoder.encode_sentence(sentence)
    category_no = net.classify(encoded_sentence)

    if category_no == 3 or category_no == 4:
        value = get_value(sentence)
        if value:
            print("\tConverted command: " + encoder.categories[category_no] + " by " + str(value))
            continue
    print("\tConverted command: " + encoder.categories[category_no])


