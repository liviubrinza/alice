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
        self.thermostat_current_temp_change_callbackFnc = None
        self.thermostat_set_temp_change_callbackFnc = None
        self.thermostat_battery_change_callbackFnc = None
        self.light_state_change_callbackFnc = None
        self.heater_state_change_callbackFnc = None

        self.current_bulb_level = 0
        self.current_thermostat_level = 0
        self.set_thermostat_level = 0
        
        self.default_luminosity_variance = 10
        self.default_heat_variance = 5
        
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
        
        self.set_bulb_level(0)
        self.set_thermostat_set_level(20)

    def set_bulb_change_value(self, value):
        """
        Sets the default value with which the light level is changed

        :param value: The new value to be used
        """
        if value and value != self.default_luminosity_variance:
            self.default_luminosity_variance = value
            print("[INFO] Set bulb change value to:", value)

    def set_temp_change_value(self, value):
        """
        Sets the default value with which the thermostat set temperature is changed

        :param value: The new value to be used
        """
        if value and value != self.default_heat_variance:
            self.default_heat_variance = value
            print("[INFO] Set temperature change value to:", value)

    def increase_bulb_level(self, change = None):
        """
        Increases the light bulbs brightness by the received value. If the value is not specified, then the default
        light change value will be used.

        :param change: the amount with which the the brightness should be increased
        """
        change = self.default_luminosity_variance if change is None else change
        new_value = self.current_bulb_level + change
        if new_value <= 100:
            self.set_bulb_level(self.current_bulb_level + change)

    def decrease_bulb_level(self, change = None):
        """
        Decreases the light bulbs brightness by the received value. If the value is not specified, then the default
        light change value will be used.

        :param change: the amount with which the the brightness should be decreased
        """
        change = self.default_luminosity_variance if change is None else change
        new_value = self.current_bulb_level - change
        if new_value >= 0:
            self.set_bulb_level(self.current_bulb_level - change)

    def set_bulb_level(self, level):
        """
        Sets the zwave light bulb node's brightness level to the given value
        :param level: The value to be set
        """
        print("[INFO] Setting bulb level to " + str(level))
        self.bulb_node.set_dimmer(self.DIMMER_COMMAND_ID, level)

    def set_bulb_color(self, color):
        """
        Sets the zwave light bulb node's RGB color to the given value.
        Before setting the value, the required "#" prefix and "0000" white level value suffix is appended
        :param color: The RGB color value to be set
        """
        color = "#" + color + "0000"
        print("[INFO] Setting bulb color to " + str(color))
        #self.bulb_node.set_rgbw(self.COLOR_COMMAND_ID, str(color))
        try:
            self.bulb_node.set_rgbw(self.COLOR_COMMAND_ID, "#FF00000000")
            time.sleep(2)
            print("COLOR VALUE: %s" % self.bulb_node.get_rgbw(self.COLOR_COMMAND_ID))
        except Exceptions as e:
            print("Exception caught: %s" % str(e))

    def increase_thermostat_set_level(self, change = None):
        """
        Increases the thermostat's set temperature by the received value. If the value is not specified, then the
        default temperature change value will be used.

        :param change: The amount with which the set temperature should be increased
        """
        change = self.default_heat_variance if change is None else change
        new_value = self.set_thermostat_level + float(change)
        print("Increasing set level to:", new_value)
        if new_value <= 30:
            self.set_thermostat_set_level(new_value)

    def decrease_thermostat_set_level(self, change = None):
        """
        Decreases the thermostat's set temperature by the received value. If the value is not specified, then the
        default temperature change value will be used.

        :param change: The amount with which the set temperature should be decreased
        :return:
        """
        change = self.default_heat_variance if change is None else change
        new_value = self.set_thermostat_level - float(change)
        print("Decreasing set level to:", new_value)
        if new_value >= 15:
            self.set_thermostat_set_level(new_value)

    def set_thermostat_set_level(self, level):
        """
        Sets the zwave thermostat node's set temperature to the given value

        :param level: The value to be set
        """
        print("[INFO] Setting thermostat set level to " + str(level))
        self.thermostat_node.set_thermostat_heating(level)

    def set_bulb_level_callback(self, callbackFnc):
        """
        Sets the function to be called in case the light bulb light level changes, if it hasn't been already set

        :param callbackFnc: The callback function to be set
        """
        if self.bulb_level_change_callbackFnc is None:
            self.bulb_level_change_callbackFnc = callbackFnc

    def set_bulb_color_callback(self, callbackFnc):
        """
        Sets the function to be called in case the light bulb color changes, if it hasn't been already set

        :param callbackFnc: The callback function to be set
        """
        if self.bulb_color_change_callbackFnc is None:
            self.bulb_color_change_callbackFnc = callbackFnc

    def set_light_state_change_callback(self, aCallbackFnc):
        """
        Sets the function to be called in case the light changes its current state(of -> off, off -> on), if it hasn't
        already been set

        :param aCallbackFnc: The callback function to be set
        """
        if self.light_state_change_callbackFnc is None:
            self.light_state_change_callbackFnc = aCallbackFnc

    def set_thermostat_current_temp_change_callback(self, callbackFnc):
        """
        Sets the function to be called in case the thermostat current temperature changes, if it hasn't been already set

        :param callbackFnc: The callback function to be set
        """
        if self.thermostat_current_temp_change_callbackFnc is None:
            self.thermostat_current_temp_change_callbackFnc = callbackFnc

    def set_thermostat_set_temp_change_callback(self, callbackFnc):
        """
        Sets the function to be called in case the thermostat set temperature changes, if it hasn't been already set

        :param callbackFnc: The callback function to be set
        """
        if self.thermostat_set_temp_change_callbackFnc is None:
            self.thermostat_set_temp_change_callbackFnc = callbackFnc

    def set_thermostat_battery_change_callback(self, callbackFnc):
        """
        Sets the function to be called in case the thermostat battery level changes, if it hasn't been already set

        :param callbackFnc: The callback function to be set
        """
        if self.thermostat_battery_change_callbackFnc is None:
            self.thermostat_battery_change_callbackFnc = callbackFnc

    def set_heater_state_change_callback(self, aCallbackFnc):
        """
        Sets the callback function to be called in case the heater changes its current state (on -> off, off -> on),
        if it hasn't already been set

        :param aCallbackFnc: The callback function to be set
        """
        if self.heater_state_change_callbackFnc is None:
            self.heater_state_change_callbackFnc = aCallbackFnc

    def handle_bulb_change(self, command_id, value):
        """
        Handles all the network changes originating from the light bulb

        :param command_id: The id of the command that changed
        :param value: The new value of the changed command
        """
        if command_id == self.DIMMER_COMMAND_ID:
            self.current_bulb_level = value
            if self.bulb_level_change_callbackFnc is not None:
                self.bulb_level_change_callbackFnc(value)
                self.light_state_change_callbackFnc("on" if value > 0 else "off")
        if command_id == self.COLOR_COMMAND_ID and self.bulb_color_change_callbackFnc is not None:
            self.bulb_color_change_callbackFnc(value)

    def handle_thermostat_change(self, command_id, value):
        """
        Handles all the network changes originating from the thermostat

        :param command_id: The id of the command that changed
        :param value: The new value of the changed command
        """
        if command_id == self.CURRENT_TEMP_ID:
            self.current_thermostat_level = value
            if self.thermostat_current_temp_change_callbackFnc is not None:
                self.thermostat_current_temp_change_callbackFnc(value)
                self.heater_state_change_callbackFnc(
                    "on" if self.current_thermostat_level < self.set_thermostat_level else "off")
        if command_id == self.THERMOSTAT_BATTERY_ID and self.thermostat_battery_change_callbackFnc is not None:
            self.thermostat_battery_change_callbackFnc(value)
        if command_id == self.SET_TEMP_ID:
            self.set_thermostat_level = value
            if self.thermostat_set_temp_change_callbackFnc is not None:
                self.thermostat_set_temp_change_callbackFnc(value)
                self.heater_state_change_callbackFnc(
                    "on" if self.current_thermostat_level < self.set_thermostat_level else "off")

    def on_zwave_value_change(self, args):
        """
        Callback function set within the python-openzwave library to be called every time a value change occurs
        on the network, regardless of the originating network node.

        :param args: Contains all the zwave relevant pieces of information regarding the change that occurred
        """
        nodeId = args["nodeId"]
        command_id = args["valueId"]["id"]
        value = args["valueId"]["value"]
        
        print()
        print("Node: %s" % nodeId)
        print("Command: %s" % command_id)
        print("Value: %s" % value)
        print()

        if nodeId == self.bulb_node.node_id:
            self.handle_bulb_change(command_id, value)
            return
        if nodeId == self.thermostat_node.node_id:
            self.handle_thermostat_change(command_id, value)
            return

    def shutdown_network(self):
        """
        Sets the light bulb's brightness to 0 and shuts down the zwave network
        """
        print("Shutting down the ZWave network")
        self.set_bulb_level(0)
        self.network.stop()

if __name__ == "__main__":
    controller = ZWaveController()
    controller.shutdown_network()
    print("Done")
