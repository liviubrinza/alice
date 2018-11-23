import signal
import sys

from MQTTController import MqttController
from NeuralNetwork import NeuralNetwork
from OneHotEncoder import OneHotEncoder

encoder = OneHotEncoder()
encoder.load_data()
net = NeuralNetwork(encoder)
mqttController = MqttController()

mapping_dict = {
    0 : "Hello there!",
    1 : "Turning on the lights",
    2 : "Turning the lights off",
    3 : "Turning the heater up",
    4 : "Turning the heater down"
    }

def get_alice_answer(command_category, value=None):
    response = mapping_dict[command_category]
    
    if(value):
        response += " by" + str(value) + " degrees"
    
    return response

def graceful_shutdown():
    print("Closing A.L.I.C.E.")
    mqttController.shutdown()
    # zwaveController.shutdownConnection()
    
def signal_handler(signal, frame):
    graceful_shutdown()
    sys.exit(0)

def get_value(sentence):
    words = sentence.split()
    for word in words:
        try:
            return int(word)
        except ValueError:
            continue
    return None

def process_input_command(command):
    # encode the input command
    encoded_sentence = encoder.encode_sentence(command)
    # retrieve the prediction from the neural network
    category_no = net.classify(encoded_sentence)
    # retrieve the command based on the prediction
    response = encoder.categories[category_no]
    # if there is any value in the command, append it
    if category_no == 3 or category_no == 4:
        value = get_value(command)
        if value:
            response = get_alice_answer(category_no, value)
        else:
            response = get_alice_answer(category)
    
    mqttController.public_response_msg(response)

mqttController.set_command_callback(process_input_command)
# net.do_training()

try:

    signal.signal(signal.SIGINT, signal_handler)

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
except Exception as e:
    print("[ERROR]: Exception caught while in the main app: %s" % str(e))
    graceful_shutdown()


