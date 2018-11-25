import signal
import sys

from MQTTController import MqttController
from NeuralNetwork import NeuralNetwork
from OneHotEncoder import OneHotEncoder
from ZwaveController import ZWaveController

encoder = OneHotEncoder()
encoder.load_data()
net = NeuralNetwork(encoder)
mqttController = MqttController()
zwaveController = ZWaveController()

response_dict = {
    0 : "Hello there!",
    1 : "Turning on the lights",
    2 : "Turning the lights off",
    3 : "Turning the heater up",
    4 : "Turning the heater down"
    }

controller_dict = {
    0 : None
}

default_light_change_level = 50
default_heat_change_level = 5

def get_alice_answer(command_category, value=None):
    response = response_dict[command_category]
    
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


def handle_zwave_command(category, value):
    print("Handle " + str(category) + " and value " + str(value))
    if category == 0:
        return

    print(controller_dict[category])
    
    if value:
        controller_dict[category](value)
    else:
        if category == 1:
            controller_dict[category](default_light_change_level)
            mqttController.publish_light_state("on")
        if category == 2:
            controller_dict[category](-default_light_change_level)
            mqttController.publish_light_state("off")
        if category == 3:
            controller_dict[category](default_heat_change_level)
            mqttController.publish_heater_state("on")
        if category == 4:
            controller_dict[category](-default_heat_change_level)
            mqttController.publish_heater_state("off")

def process_input_command(command):
    # encode the input command
    encoded_sentence = encoder.encode_sentence(command)
    # retrieve the prediction from the neural network
    category_no = net.classify(encoded_sentence)
    # retrieve the command based on the prediction
    response = encoder.categories[category_no]
    value = None
    # if there is any value in the command, append it
    if category_no == 3 or category_no == 4:
        value = get_value(command)

    # this for UI purposes
    response = get_alice_answer(category_no, value)
    mqttController.public_response_msg(response)

    handle_zwave_command(category_no, value)

def trigger_color_change(msg):
    msg = msg.upper()
    print("Color change received: " + str(msg))
    zwaveController.set_bulb_color(msg)

mqttController.set_command_callback(process_input_command)
mqttController.set_color_change_callback(trigger_color_change)
# set the callbacks between zwave and mqtt
zwaveController.set_bulb_level_callback(mqttController.publish_light_level)
zwaveController.set_bulb_color_callback(None)
zwaveController.set_thermostat_level_callback(None)
# set the zwave controller trigger methods
controller_dict[1] = zwaveController.set_bulb_level
controller_dict[2] = zwaveController.set_bulb_level
controller_dict[3] = zwaveController.set_thermostat_level
controller_dict[4] = zwaveController.set_thermostat_level

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


