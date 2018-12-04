import json
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


def get_alice_answer(command_category, value=None):
    response = response_dict[command_category]
    
    if(value):
        response += " by" + str(value) + " degrees"
    
    return response

def graceful_shutdown():
    print("Closing A.L.I.C.E.")
    mqttController.shutdown()
    zwaveController.shutdown_network()
    
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
    if category == 0:
        return
    
    if value:
        controller_dict[category](value)
    else:
        controller_dict[category]()


def change_configuration(value):
    print("New configuration change received: ", str(value))
    configuration_json = json.loads(value)
    new_config_sender = configuration_json['sender']
    new_config_value = configuration_json['value']
    if new_config_sender == 'lightLevel':
        zwaveController.set_bulb_level(new_config_value)
    elif new_config_sender == 'lightingStep':
        zwaveController.set_bulb_change_value(new_config_value)
    elif new_config_sender == 'heatingStep':
        zwaveController.set_temp_change_value(new_config_value)

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
    mqttController.publish_response_msg(response)

    handle_zwave_command(category_no, value)

def trigger_color_change(msg):
    msg = msg.upper()
    zwaveController.set_bulb_color(msg)

# set the callbacks from mqtt
mqttController.set_command_callback(process_input_command)
mqttController.set_color_change_callback(trigger_color_change)
mqttController.set_configuration_callback(change_configuration)
# set the callbacks between zwave and mqtt
zwaveController.set_bulb_level_callback(mqttController.publish_light_level)
zwaveController.set_bulb_color_callback(None)
zwaveController.set_thermostat_current_temp_change_callback(mqttController.publish_current_temperature)
zwaveController.set_thermostat_set_temp_change_callback(mqttController.publish_set_temperature)
zwaveController.set_thermostat_battery_change_callback(mqttController.publish_battery_level)
zwaveController.set_light_state_change_callback(mqttController.publish_light_state)
zwaveController.set_heater_state_change_callback(mqttController.publish_heater_state)

# send the initial configuration values over mqtt
mqttController.publish_initial_config(zwaveController.get_configuration_values())

# set the zwave controller trigger methods
controller_dict[1] = zwaveController.increase_bulb_level
controller_dict[2] = zwaveController.decrease_bulb_level
controller_dict[3] = zwaveController.increase_thermostat_set_level
controller_dict[4] = zwaveController.decrease_thermostat_set_level

try:
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        sentence = input("Enter command:")
        if sentence == "quit":
            break
except Exception as e:
    print("[ERROR]: Exception caught while in the main app: %s" % str(e))
    graceful_shutdown()


