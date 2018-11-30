import time

from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption


class ZWaveController:

    DIMMER_COMMAND_ID     = None
    COLOR_COMMAND_ID      = None
    THERMOSTAT_BATTERY_ID = None
    CURRENT_TEMP_ID       = None
    SET_TEMP_ID           = None
    
    def __init__(self):
        print("[INFO] Initializing zwave network controller")
        self.bulb_node = None
        self.thermostat_node = None

        self.options = ZWaveOption(device='/dev/ttyACM0', config_path="/home/pi/.local/lib/python3.5/site-packages/python_openzwave/ozw_config", user_path='.')
        self.options.set_log_file("ZwaveController_log.log")
        self.options.set_append_log_file(True)
        self.options.set_console_output(False)
        self.options.set_save_log_level('Debug')
        self.options.set_logging(True)
        self.options.lock()

        self.network = ZWaveNetwork(self.options, log=None)

        self.bulb_level_change_callbackFnc = None
        self.bulb_color_change_callbackFnc = None
        self.thermostat_level_change_callbackFnc = None

        for i in range(6):
            time.sleep(1)
            if self.network.state >= self.network.STATE_AWAKED:
                print("[INFO] Network is awake")
                break

        print("[INFO] Nodes in network : {}".format(self.network.nodes_count))
    
        for i in range(6):
            time.sleep(1)
            if self.network.state == self.network.STATE_READY:
                break
    
        if self.network.state == self.network.STATE_READY:
            print("[INFO] Network is set up and ready")
        elif self.network.state == self.network.STATE_AWAKED:
            print("[WARN] Network is awake. Some sleeping devices may still be missing")
        else:
            print("[WARN] Network is still starting. You MUST increase timeout. But will continue.")

        if self.network.setValueChangeCallbackFnc(self.on_zwave_value_change):
            print("[INFO] Callback successfully set")
        else:
            print("[INFO] Callback not set correctly")
        
        for i in self.network.nodes.keys():
            current_node = self.network.nodes[i]
            if current_node.product_name.startswith("Bulb"):
                self.bulb_node = current_node
                print("[INFO] Found the bulb on the network with ID:",current_node._object_id)
            elif current_node.product_name.startswith("Popp"):
                self.thermostat_node = current_node
                print("[INFO] Found the thermostat on the network with ID:", current_node._object_id)

        # Find all the required configuration command ids for the bulb
        bulb_dict = self.bulb_node.to_dict()
        bulb_value_keyset = bulb_dict["values"].keys()
        for value in bulb_value_keyset:
            value_dict = bulb_dict["values"][value]
            # try to find all the command values required
            if value_dict["label"] == "Level":
                self.DIMMER_COMMAND_ID = value_dict["value_id"]
                print("Found bulb level command: ",self.DIMMER_COMMAND_ID)
        
        # Find all the required configuration command ids for the thermostat
        thermostat_dict = self.thermostat_node.to_dict()
        thermostat_value_keyset = thermostat_dict["values"].keys()
        for value in thermostat_value_keyset:
            value_dict = thermostat_dict["values"][value]
            # try to find all the command values required
            value_label = value_dict["label"]
            if value_label == "Battery Level":
                self.THERMOSTAT_BATTERY_ID = value_dict["value_id"]
                print("Found thermostat battery level: ", self.THERMOSTAT_BATTERY_ID)
            elif value_label == "Temperature":
                self.CURRENT_TEMP_ID = value_dict["value_id"]
                print("Found thermostat current temperature: ", self.CURRENT_TEMP_ID)
            elif value_label == "Heating 1":
                self.SET_TEMP_ID = value_dict["value_id"]
                print("Found thermostat set temperature: ", self.SET_TEMP_ID)

    def set_bulb_level(self, level):
        print("[INFO] Setting bulb level to " + str(level))
        self.bulb_node.set_dimmer(self.DIMMER_COMMAND_ID, level)

    def set_bulb_color(self, color):
        color = "#" + color + "0000"
        print("[INFO] Setting bulb color to " + str(color))
        #self.bulb_node.set_rgbw(self.COLOR_COMMAND_ID, str(color))
        try:
                self.bulb_node.set_rgbw(self.COLOR_COMMAND_ID, "#FF00000000")
                time.sleep(2)
                print("COLOR VALUE: %s" % self.bulb_node.get_rgbw(self.COLOR_COMMAND_ID))
        except Exceptions as e:
                print("Exception caught: %s" % str(e))

    def set_thermostat_level(self, level):
        print("[INFO] Setting thermostat level to " + str(level))
        pass

    def set_bulb_level_callback(self, callbackFnc):
        self.bulb_level_change_callbackFnc = callbackFnc

    def set_bulb_color_callback(self, callbackFnc):
        self.bulb_color_change_callbackFnc = callbackFnc

    def set_thermostat_level_callback(self, callbackFnc):
        self.thermostat_level_change_callbackFnc = callbackFnc

    def handle_bulb_change(self, command_id, value):
        if command_id == self.DIMMER_COMMAND_ID and self.bulb_level_change_callbackFnc is not None:
            self.bulb_level_change_callbackFnc(value)
        if command_id == self.COLOR_COMMAND_ID and self.bulb_color_change_callbackFnc is not None:
            self.bulb_color_change_callbackFnc(value)

    def handle_thermostat_change(self, command_id, value):
        if command_id == self.CURRENT_TEMP_ID and self.thermostat_level_change_callbackFnc is not None:
            self.thermostat_level_change_callbackFnc(value)
            print("Sent new temp to main")
        if command_id == self.THERMOSTAT_BATTERY_ID and self.thermostat_battery_change_callbackFnc is not None:
            self.thermostat_battery_change_callbackFnc(value)
            print("Sent new battery to main")
        if command_id == self.SET_TEMP_ID and self.thermostat_set_level_change_callbackFnc is not None:
            self.thermostat_set_level_change_callbackFnc(value)
            print("Sent new set temp to main")

    def on_zwave_value_change(self, args):
        nodeId = args["nodeId"]
        command_id = args["valueId"]["id"]
        value = args["valueId"]["value"]
        
        print()
        print("Node: %s" % args["nodeId"])
        print("Command: %s" % args["valueId"]["id"])
        print("Value: %s" % args["valueId"]["value"])
        print()

        if nodeId == self.bulb_node.node_id:
            self.handle_bulb_change(command_id, value)
            return
        if nodeId == self.thermostat_node.node_id:
            self.handle_thermostat_change(command_id, value)
            return

    def shutdown_network(self):
        print("Shutting down the ZWave network")
        self.set_bulb_level(0)
        self.network.stop()

if __name__ == "__main__":
    controller = ZWaveController()
    controller.shutdown_network()
    print("Done")
