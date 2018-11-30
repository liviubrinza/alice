import time
import json

from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption


class ZWaveController:

    DIMMER_COMMAND_ID = 72057594076299265
    COLOR_COMMAND_ID  = 72057594076512263
    
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
            
        node_id_list = self.network.nodes.keys()
        
        for i in node_id_list:
            current_node = self.network.nodes[i]
            if current_node.product_name.startswith("Bulb"):
                self.bulb_node = current_node
                print("[INFO] Found the bulb on the network with ID:",current_node._object_id)
            elif current_node.product_name.startswith("Popp"):
                self.thermostat_node = current_node
                print("[INFO] Found the thermostat on the network with ID:", current_node._object_id)

        print("Initial node structure of Bulb:")
        print()
        bulb_dict = self.bulb_node.to_dict()
        print(bulb_dict.keys())
        print()
        print("Bulb values:")
        print("============")
        bulb_value_keyset = bulb_dict["values"].keys()
        for value in bulb_value_keyset:
            print("Value:",value)
            value_dict = bulb_dict["values"][value]
            print(json.dumps(value_dict, indent=2))
            # try to find all the command values required
            if value_dict["label"] == "Level":
                    bulb_level_command = value_dict["value_id"]
                    print("Found bulb level: ",bulb_level_command)
        
        print()
        print("Initial node structure of Thermostat:")
        print()
        thermostat_dict = self.thermostat_node.to_dict()
        print(thermostat_dict.keys())
        print()
        print("Thermostat values:")
        print("==================")
        thermostat_value_keyset = thermostat_dict["values"].keys()
        for value in thermostat_value_keyset:
            print("Value: ",value)
            value_dict = thermostat_dict["values"][value]
            print(json.dumps(value_dict, indent=2))
            # try to find all the command values required
            value_label = value_dict["label"]
            if value_label == "Battery Level":
                thermostat_battery_command = value_dict["value_id"]
                print("Found thermostat battery level: ", thermostat_battery_command)
            elif value_label == "Temperature":
                thermostat_current_temperature_commmand = value_dict["value_id"]
                print("Found thermostat current temperature: ", thermostat_current_temperature_commmand)
            elif value_label == "Heating 1":
                thermostat_set_temperature_command = value_dict["value_id"]
                print("Found thermostat set temperature: ", thermostat_set_temperature_command)
            
                
        #self.bulb_node.set_dimmer(self.DIMMER_COMMAND_ID, 10)
        #time.sleep(3)
        
        #print("Initial node structure")
        #print()
        #print(self.bulb_node.to_dict())
        #print()

        #time.sleep(3)
        #print("DIMMER LEVEL: %s" % self.bulb_node.get_dimmer_level(self.DIMMER_COMMAND_ID))
        
        #time.sleep(3)
        #self.bulb_node.set_dimmer(self.DIMMER_COMMAND_ID, 0)
        #print()
        #print()
        #print(self.bulb_node.to_dict())

    def on_zwave_value_change(self, args):
        print()
        print("Node: %s" % args["nodeId"])
        print("Command: %s" % args["valueId"]["id"])
        print("Value: %s" % args["valueId"]["value"])
        print()

    def shutdown_network(self):
        print("Shutting down the ZWave network")
        self.network.stop()

if __name__ == "__main__":
    controller = ZWaveController()
    controller.shutdown_network()
    print("Done")
