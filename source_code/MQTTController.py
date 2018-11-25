import paho.mqtt.client as mqtt

class MqttController:

    INPUT_COMMAND_TOPIC = "inputCommand"
    OUTPUT_RESPONSE_TOPIC = "outputResponse"
    OUTPUT_LIGHT_STATE_TOPIC = "lightState"
    OUTPUT_HEATER_STATE_TOPIC = "heaterState"
    OUTPUT_LIGHT_LEVEL_TOPIC = "lightLevel"
    OUTPUT_HEAT_LEVEL_TOPIC = "heatLevel"

    def __init__(self):
        self.mqtt_client = mqtt.Client("alice_client")
        self.mqtt_client.on_message=self.on_msg_received
        self.mqtt_client.connect("localhost")
        self.mqtt_client.loop_start()

        self.commandCallbackFnc = None

        self.subscribe_to_topics()
        print("[INFO] Mqtt controller up and running")

    def set_command_callback(self, aCallback):
        if self.commandCallbackFnc is None:
            self.commandCallbackFnc = aCallback
            print("[INFO] Successfully set command callback function")
            return True
        print("[WARN]: Command callback function could not be set")
        return False

    def subscribe_to_topics(self):
        self.mqtt_client.subscribe(self.INPUT_COMMAND_TOPIC)

    def on_msg_received(self, client, userdata, message):
        msg = str(message.payload.decode("UTF-8"))
        topic = message.topic

        if topic == self.INPUT_COMMAND_TOPIC and self.commandCallbackFnc:
            self.commandCallbackFnc(msg)

    def public_response_msg(self, message):
        self.mqtt_client.publish(self.OUTPUT_RESPONSE_TOPIC, message)

    def publish_light_state(self, state):
        self.mqtt_client.publish(self.OUTPUT_LIGHT_STATE_TOPIC, state)

    def publish_heater_state(self, state):
        self.mqtt_client.publish(self.OUTPUT_HEATER_STATE_TOPIC, state)

    def publish_light_level(self, level):
        self.mqtt_client.publish(self.OUTPUT_LIGHT_LEVEL_TOPIC, level)

    def publish_heat_level(self, leve):
        self.mqtt_client.publish(self.OUTPUT_HEAT_LEVEL_TOPIC, level)

    def shutdown(self):
        self.mqtt_client.loop_stop()
