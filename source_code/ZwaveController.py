from openzwave.node import ZWaveNode
from openzwave.option import ZWaveOption
from openzwave.network import ZWaveNetwork
import time

class ZWaveController:

    DIMMER_LEVEL_VAL = 72057594076299265
    COLOR_LEVEL_VAL  = 72057594076512263
    
    def __init__(self):
        print("Initializing zwave network controller")
        self.bulb_node = None
        self.door_sensor = None

        self.options = ZWaveOption(device='/dev/ttyACM0', config_path="/home/pi/.local/lib/python3.5/site-packages/python_openzwave/ozw_config", user_path='.')
        self.options.set_log_file("ZwaveController_log.log")
        self.options.set_append_log_file(True)
        self.options.set_console_output(False)
        self.options.set_save_log_level('Debug')
        self.options.set_logging(True)
        self.options.lock()

        print("Start network")
        self.network = ZWaveNetwork(self.options, log=None)

        delta = 0.5
        for i in range(6):
            time.sleep(1)
            if self.network.state >= self.network.STATE_AWAKED:
                break
    
        print("-------------------------------------------------------------------------------")
        print("Network is awaked. Talk to controller.")
        print("Nodes in network : {}".format(self.network.nodes_count))
    
        for i in range(6):
            time.sleep(1)
            if self.network.state == self.network.STATE_READY:
                break
    
        if self.network.state == self.network.STATE_READY:
            print("Network is ready. Get nodes")
        elif self.network.state == self.network.STATE_AWAKED:
            print("Network is awake. Some sleeping devices may miss. You can increase timeout to get them. But will continue.")
        else:
            print("Network is still starting. You MUST increase timeout. But will continue.")
    
       # for node in self.network.nodes:
       #     print("------------------------------------------------------------")
       #     print("{} - Name : {} ( Location : {} )".format(self.network.nodes[node].node_id, self.network.nodes[node].name, self.network.nodes[node].location))
       #     print(" {} - Ready : {} / Awake : {} / Failed : {}".format(self.network.nodes[node].node_id, self.network.nodes[node].is_ready, self.network.nodes[node].is_awake, self.network.nodes[node].is_failed))
       #     print(" {} - Manufacturer : {}  ( id : {} )".format(self.network.nodes[node].node_id, self.network.nodes[node].manufacturer_name, self.network.nodes[node].manufacturer_id))
       #     print(" {} - Product : {} ( id  : {} / type : {} / Version : {})".format(self.network.nodes[node].node_id, self.network.nodes[node].product_name, self.network.nodes[node].product_id, self.network.nodes[node].product_type, self.network.nodes[node].version))
       #     print(" {} - Command classes : {}".format(self.network.nodes[node].node_id, self.network.nodes[node].command_classes_as_string))
       #     print(" {} - Capabilities : {}".format(self.network.nodes[node].node_id, self.network.nodes[node].capabilities))
       #     print(" {} - Neighbors : {} / Power level : {}".format(self.network.nodes[node].node_id, self.network.nodes[node].neighbors, self.network.nodes[node].get_power_level()))
       #     print(" {} - Is sleeping : {} / Can wake-up : {} / Battery level : {}".format(self.network.nodes[node].node_id, self.network.nodes[node].is_sleeping, self.network.nodes[node].can_wake_up(), self.network.nodes[node].get_battery_level()))

        if self.network.setValueChangeCallbackFnc(self.on_zwave_value_change):
                print("Callback successfully set")
        else:
                print("Callback not set correctly")
        
        self.bulb_node = self.network.nodes[2]
        self.bulb_node.set_dimmer(self.DIMMER_LEVEL_VAL, 50)
        print()
        time.sleep(3)
        print("DIMMER LEVEL: %s" % self.bulb_node.get_dimmer_level(self.DIMMER_LEVEL_VAL))
        
        self.bulb_node.set_rgbw(self.COLOR_LEVEL_VAL, "#FFFFFFFFFF")
        time.sleep(3)
        self.bulb_node.set_rgbw(self.COLOR_LEVEL_VAL, "#FFFFFFFF00")
        time.sleep(3)
        self.bulb_node.set_rgbw(self.COLOR_LEVEL_VAL, "#FFFFFF00FF")
        
        #self.bulb_node.set_rgbw(self.COLOR_LEVEL_VAL, 10)
        print("COLOR VALUE: %s" % self.bulb_node.get_rgbw(self.COLOR_LEVEL_VAL)) 
         
        time.sleep(3)
        self.bulb_node.set_dimmer(self.DIMMER_LEVEL_VAL, 0)
        print()
        print()
        #print(self.bulb_node.to_dict())

    def on_zwave_value_change(self, args):
        nodeId = args["nodeId"]
        command_id = args["valueId"]["id"]
        value = args["valueId"]["value"]
        
        print()
        print("Node id: %s" % nodeId)
        print("Command id: %s" % command_id)
        print("Value: %s" % value)
        print()

    def shutdown_network(self):
        print("Shutting down the ZWave network")
        self.network.stop()

if __name__ == "__main__":
    controller = ZWaveController()
    controller.shutdown_network()
    print("Done")
