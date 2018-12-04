import paho.mqtt.client as mqtt
import json

class MqttController:

    # MQTT topic constants
    INPUT_COMMAND_TOPIC = "inputCommand"
    INPUT_COLOR_CHANGE_TOPIC = "colorChange"
    INPUT_CONFIGURATION_TOPIC = "configuration"
    OUTPUT_RESPONSE_TOPIC = "outputResponse"
    OUTPUT_LIGHT_STATE_TOPIC = "lightState"
    OUTPUT_HEATER_STATE_TOPIC = "heaterState"
    OUTPUT_SET_TEMP_TOPIC = "setTemperature"
    OUTPUT_CURRENT_TEMP_TOPIC = "currentTemperature"
    OUTPUT_LIGHT_LEVEL_TOPIC = "lightLevel"
    OUTPUT_BATTERY_LEVEL_TOPIC = "batteryLevel"
    OUTPUT_INITIAL_CONFIG_TOPIC = "initialConfig"

    def __init__(self):
        """
        Initialize the mqtt controller, subscribe to all the required topics
        """
        self.mqtt_client = mqtt.Client("alice_client")
        self.mqtt_client.on_message=self.on_msg_received
        self.mqtt_client.connect("localhost")
        self.mqtt_client.loop_start()

        # MQTT input callback methods
        self.commandCallbackFnc = None
        self.colorChangeCallbackFnc = None
        self.configurationCallbackFnc = None

        self.subscribe_to_topics()
        print("[INFO] <MqttController> Mqtt controller up and running")

    def set_command_callback(self, aCallback):
        """
        Sets the callback function to call when a command is received over MQTT

        :param aCallback: the callback function to set
        :return: True - callback successfully set
                 False - otherwise
        """
        if self.commandCallbackFnc is None:
            self.commandCallbackFnc = aCallback
            print("[INFO] <MqttController> Successfully set command callback function")
            return True
        print("[WARN] <MqttController> Command callback function was already set")
        return False
        
    def set_color_change_callback(self, aCallback):
        """
        Sets the callback function to call when a color change is received over MQTT

        :param aCallback: the callback function to set
        :return: True - callback successfully set
                 False - otherwise
        """
        if self.colorChangeCallbackFnc is None:
            self.colorChangeCallbackFnc = aCallback
            print("[INFO] <MqttController> Successfully set the color change callback function")
            return True
        print("[WARN] <MqttController> Color change callback function was already set")
        return False

    def set_configuration_callback(self, aCallback):
        """
        Sets the callback function to call when a configuration change is received over MQTT

        :param aCallback: the callback function to set
        :return: True - callback successfully set
                 False - otherwise
        """
        if self.configurationCallbackFnc is None:
            self.configurationCallbackFnc = aCallback
            print("[INFO] <MqttController> Successfully set the configuration callback function")
            return True
        print("[WARN] <MqttController> Configuration callback function was already set")

    def subscribe_to_topics(self):
        """
        Subscribes to all the MQTT input topics
        """
        self.mqtt_client.subscribe(self.INPUT_COMMAND_TOPIC)
        self.mqtt_client.subscribe(self.INPUT_COLOR_CHANGE_TOPIC)
        self.mqtt_client.subscribe(self.INPUT_CONFIGURATION_TOPIC)

    def on_msg_received(self, client, userdata, message):
        """
        Handles all input messages received over the subscribed topics

        :param client:
        :param userdata:
        :param message:
        :return:
        """
        msg = str(message.payload.decode("UTF-8"))
        topic = message.topic

        if topic == self.INPUT_COMMAND_TOPIC and self.commandCallbackFnc:
            self.commandCallbackFnc(msg)
        if topic == self.INPUT_COLOR_CHANGE_TOPIC and self.colorChangeCallbackFnc:
            self.colorChangeCallbackFnc(msg)
        if topic == self.INPUT_CONFIGURATION_TOPIC and self.configurationCallbackFnc:
            self.configurationCallbackFnc(msg)

    def publish_response_msg(self, message):
        """
        Publishes the received message over the MQTT response topic

        :param message: the response message to publish
        """
        self.mqtt_client.publish(self.OUTPUT_RESPONSE_TOPIC, message)

    def publish_light_state(self, state):
        """
        Publishes the received light state over the required MQTT topic

        :param state: String representation of the current light state ("on" / "off")
        """
        self.mqtt_client.publish(self.OUTPUT_LIGHT_STATE_TOPIC, state)

    def publish_heater_state(self, state):
        """
        Publishes the received heater state over the required MQTT topic

        :param state: String representation of the current heater state ("on" / "off")
        """
        self.mqtt_client.publish(self.OUTPUT_HEATER_STATE_TOPIC, state)

    def publish_light_level(self, level):
        """
        Publishes the current light level over the required MQTT topic

        :param level: The current light level value
        """
        self.mqtt_client.publish(self.OUTPUT_LIGHT_LEVEL_TOPIC, level)

    def publish_current_temperature(self, temperature):
        """
        Publishes the current temperature over the required MQTT topic

        :param temperature: The current temperature read by the thermostat (in degrees Celsius)
        """
        self.mqtt_client.publish(self.OUTPUT_CURRENT_TEMP_TOPIC, temperature)

    def publish_set_temperature(self, temperature):
        """
        Publishes the set temperature over the required MQTT topic

        :param temperature: The set temperature set on the thermostat (in degrees Celsius)
        """
        self.mqtt_client.publish(self.OUTPUT_SET_TEMP_TOPIC, temperature)

    def publish_battery_level(self, level):
        """
        Publishes the current thermostat battery status over the required MQTT topic

        :param status: The current status (value) of the thermostat's battery level
        """
        self.mqtt_client.publish(self.OUTPUT_BATTERY_LEVEL_TOPIC, level)
        
    def publish_initial_config(self, config):
        """
        Publishes the initial configuration values dictionary upon system startup
        
        :param config: The dictionary containing the initial configuration values
        """
        self.mqtt_client.publish(self.OUTPUT_INITIAL_CONFIG_TOPIC, json.dumps(config))

    def shutdown(self):
        """
        Shuts down the MQTT controller by stopping the MQTT listening loop
        (i.e. it disconnects from the MQTT message broker)
        """
        self.mqtt_client.loop_stop()
