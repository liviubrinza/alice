from openzwave.node import ZWaveNode
from openzwave.option import ZWaveOption
from openzwave.network import ZWaveNetwork
import time


class ZWaveController:
    
    def __init__(self):
        print("Initializing zwave network controller")
        self.bulb_node = None
        self.door_sensor = None
		
        self.options = ZWaveOption(device='/dev/ttyACM0', config_path='/home/pi/.local/lib/python3.5/site-packages/python_openzwave/ozw_config/config', user_path='.', cmd_line='')
        self.options.set_append_log_file(True)
        self.options.set_console_output(True)
        self.options.set_save_log_level('Warning')
        self.options.set_logging(True)
        self.options.lock()
        print("INFO: Locked options")
        self.network = ZWaveNetwork(self.options, log=None)
        print("INFO: Created ZwaveNetwork")
        print("Network state: " + str(self.network.state) + " stopped state: " + str(self.network.STATE_STOPPED))

        if self.network.state >= self.network.STATE_STOPPED:
            print("WARNING: Network was not stopped. Restarting now")
            self.network.destroy()
            time.sleep(5.0)
		
            self.network.start()
            
            #try for 10 seconds to wake the network up
            for i in range(0, 20):
                if self.network.state >= self.network.STATE_AWAKED:
                    # network is awake, move on
                    break
                else:
                    # network is still not awaken, let's wait a bit and then try again
                    time.sleep(1.0)
                
            if self.network.state < self.network.STATE_AWAKED:
                print("WARNING: COULD NOT WAKE UP THE ZWAVE NETWORK")
                self.network.stop()
                return
            else:
                print("Network awake")
            
            for i in range(0, 10):
                if self.network.state >= self.network.STATE_READY:
                    # network is ready for interacting
                    break
                else:
                    # network not yet ready, wait a bit and then try again
                    time.sleep(1.0)
                
            if not self.network.is_ready:
                print("WARNING: NETWORK IS NOT READY FOR INTERACTING")
                print("Current state is: %s" % self.network.state_str)
            else:
                print("Network Ready")
            
            print("Network:")
            print(self.network.nodes)
		
            self.network.stop()
		
if __name__ == "__main__":
    controller = ZWaveController()
		
##		self.bulb_node = self.network.nodes[2]
##		self.door_sensor = self.network.nodes[3]
##		self.multi_sensor = self.network.nodes[4]
##		
##		self.bulb_node.set_rgbw(self.__COLOR_VAL, self.__NORMAL_WHITE)
##		self.bulb_node.set_dimmer(self.__DIMMER_LEVEL_VAL, 200)
##		time.sleep(2.0)
##		self.bulb_node.set_dimmer(self.__DIMMER_LEVEL_VAL, 0)
##		
##		self.network.set_poll_interval()
##		
##		# request to update the multisensor information
##		self.triggerMultiUpdate()
		
##	def triggerMultiUpdate(self):
##		self.multi_sensor.request_state()

##	def setValueChangeCallbackFnc(self, aCallback):
##		return self.network.setValueChangeCallbackFnc(aCallback)				
##		
##	def getBulbNodeId(self):
##		return self.bulb_node.node_id
##		
##	def getDoorSensorNodeId(self):
##		return self.door_sensor.node_id
##		
##	def getMultiSensorNodeId(self):
##		return self.multi_sensor.node_id
##
##	def getMotionCommandId(self):
##		return self.__MOTION_VAL
##		
##	def getLuminesenceCommandId(self):
##		return self.__LUMINESENCE
##		
##	def getHumidityCommandId(self):
##		return self.__HUMIDITY
##		
##	def getTemperatureCommandId(self):
##		return self.__TEMPERATURE
##		
##	def getUvCommandId(self):
##		return self.__ULTRAVIOLET
##	
##	def getDimmerCommandId(self):
##		return self.__DIMMER_LEVEL_VAL
##		
##	
##	def shutdownNetwork(self):
##		print("Shutting down zwave network controller")
##		self.network.stop()
##
##	def setBulbColor(self, aValue):
##		if aValue == "cold":
##			self.setColdWhite()
##		elif aValue == "warm":
##			self.setWarmWhite()
##		else:
##			self.bulb_node.set_rgbw(self.__COLOR_VAL, "#" + aValue + "0000")
##
##	def setWarmWhite(self):
##		self.bulb_node.set_rgbw(self.__COLOR_VAL, self.__WARM_WHITE)
##
##	def setColdWhite(self):
##		self.bulb_node.set_rgbw(self.__COLOR_VAL, self.__COLD_WHITE)
##
##	def setCurrentBulbColor(self):
##		setBulbColor(self.currentColor)
##
##	def getCurrentColor(self):
##		return self.currentColor
##
##	def setBulbDimmer(self, aValue):
##		self.bulb_node.set_dimmer(self.__DIMMER_LEVEL_VAL, aValue)

# TEST PART FOR THE SCRIPT #
"""
try:
	z = ZWaveController()
	## Get door sensor battery level ##
#	sensor = z.network.nodes[3]
#	print(str(sensor))
#	time.sleep(2.0)
#	print("Battery level : %s " % sensor.get_battery_level())

	multi = z.network.nodes[4]
	print(str(multi))

	time.sleep(2.0)
	z.shutdownNetwork()
	time.sleep(2.0)
except Exception as e:
	print("ERROR: Exception caught in main app: %s" % str(e))
	z.shutdownNetwork()
"""
