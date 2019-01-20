import json
import random
import signal
import sys
import threading
import time

from MQTTController import MqttController
from NeuralNetwork import NeuralNetwork
from OneHotEncoder import OneHotEncoder
from ZwaveController import ZWaveController
from constants import responses

encoder = OneHotEncoder()
encoder.load_data()
net = NeuralNetwork(encoder)
mqttController = MqttController()
zwaveController = ZWaveController()

controller_dict = {
    0 : None,
    1 : zwaveController.increase_bulb_level,
    2 : zwaveController.decrease_bulb_level,
    3 : zwaveController.increase_thermostat_set_level,
    4 : zwaveController.decrease_thermostat_set_level
}

system_active = False

"""========== System shutdown =========="""
def graceful_shutdown():
    global system_active
    print("Closing A.L.I.C.E.")
    system_active = False
    mqttController.shutdown()
    zwaveController.shutdown_network()

def signal_handler(signal, frame):
    graceful_shutdown()
    sys.exit(0)

"""========== Lifecycle ping =========="""
def lifecycle_ping():
    while system_active:
        mqttController.publish_lifecycle_ping()
        time.sleep(4)

def get_alice_answer(command_category, value=None):
    response = random.choice(responses[command_category])
    response_suffix = ""

    if value:
        # light related change
        if command_category == 1 or command_category == 2:
            response_suffix = "by" + str(value) + " percent"
        if command_category == 3 or command_category == 4:
            response_suffix = "by" + str(value) + " degrees"

        response += response_suffix
    
    return response

def get_value_from_command(command):
    words = command.split()
    for word in words:
        try:
            return int(word)
        except ValueError:
            continue
    return None

def handle_zwave_command(category, value):
    if category == -1 or category == 0:
        return
    controller_dict[category](value)

def process_input_command(command):
    # encode the input command
    encoded_sentence = encoder.encode_sentence(command)
    # retrieve the prediction from the neural network
    category_no, guess_list = net.classify(encoded_sentence)
    # if there is any value in the command, append it
    value = get_value_from_command(command)
    # this for UI purposes
    response = get_alice_answer(category_no, value)
    mqttController.publish_response_msg(response)

    handle_zwave_command(category_no, value)

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

# TODO: CHECK WHETHER THIS WILL WORK
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

try:
    signal.signal(signal.SIGINT, signal_handler)
    system_active = True
    threading.Thread(target=lifecycle_ping).start()

    while True:
        sentence = input("Enter command:")
        if sentence == "quit":
            break
except Exception as e:
    print("[ERROR]: Exception caught while in the main app: %s" % str(e))
    graceful_shutdown()


