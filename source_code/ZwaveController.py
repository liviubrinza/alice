import time

from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption


class ZWaveController:

    DIMMER_COMMAND_ID = 72057594076299265
    COLOR_COMMAND_ID  = 72057594076512263
    
    def __init__(self):
        print("[INFO] Initializing zwave network controller")
        self.bulb_node = None
        self.thermostat = None

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
        
        self.bulb_node = self.network.nodes[2]

        # self.bulb_node.set_dimmer(self.DIMMER_LEVEL_VAL, 50)
        # print()
        # time.sleep(3)
        # print("DIMMER LEVEL: %s" % self.bulb_node.get_dimmer_level(self.DIMMER_LEVEL_VAL))
        #
        # self.bulb_node.set_rgbw(self.COLOR_LEVEL_VAL, "#FFFFFFFFFF")
        # time.sleep(3)
        # self.bulb_node.set_rgbw(self.COLOR_LEVEL_VAL, "#FFFFFFFF00")
        # time.sleep(3)
        # self.bulb_node.set_rgbw(self.COLOR_LEVEL_VAL, "#FFFFFF00FF")
        #
        # #self.bulb_node.set_rgbw(self.COLOR_LEVEL_VAL, 10)
        # print("COLOR VALUE: %s" % self.bulb_node.get_rgbw(self.COLOR_LEVEL_VAL))
        #
        # time.sleep(3)
        # self.bulb_node.set_dimmer(self.DIMMER_LEVEL_VAL, 0)
        # print()
        # print()
        #print(self.bulb_node.to_dict())

    def set_bulb_level(self, level):
        print("[INFO] Setting bulb level to " + str(level))
        self.bulb_node.set_dimmer(self.DIMMER_COMMAND_ID, level)

    def set_bulb_color(self, color):
        color = "#" + color + "0000"
        print("[INFO] Setting bulb color to " + str(color))
        self.bulb_node.set_rgbw(self.COLOR_COMMAND_ID, str(color))

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
        pass

    def on_zwave_value_change(self, args):
        nodeId = args["nodeId"]
        command_id = args["valueId"]["id"]
        value = args["valueId"]["value"]
        
        print("NODE ID: " + nodeId)
        print("COMMAND ID: " + command_id)
        print("VALUE: " + value)

        if nodeId == self.bulb_node.node_id:
            self.handle_bulb_change(command_id, value)
            return
        if nodeId == self.thermostat.node_id:
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
