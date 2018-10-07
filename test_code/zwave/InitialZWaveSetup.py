# location relevant modules
from astral import Location
# zwave relevant modules
from openzwave.node import ZWaveNode
from openzwave.option import ZWaveOption
from openzwave.network import ZWaveNetwork
# MQTT relevant modules
import paho.mqtt.client as mqtt
# others
from pathlib import Path
import json
import requests
import time
import datetime
import sys
import threading
import signal

##### HELPER DOODADS #######

printDots = True

def printWaitingDots():
	global printDots

	while printDots:
		sys.stdout.write(".")
		sys.stdout.flush()
		time.sleep(1.0)

	printDots = True

###### LOCATION SPECIFIC PART ###########

# location relevant info
LOCATION_FILE = "location.json"
locationInfo = {
	"latitude"  : "",
	"longitude" : "",
	"timezone"  : "",
	"country"   : "",
	"county"    : "",
	"town"      : "",
	"dawn"      : "",
	"dusk"      : ""}

# will contain all the required sun position information
sunInfo = {}
color_change_time = datetime.time(hour=0, minute=0, second=0, microsecond=0)

def getSunInformation():
	if not loadLocationFile():
		r = requests.get('http://freegeoip.net/json')
		js = r.json()
		locationInfo["latitude"]  = js["latitude"]
		locationInfo["longitude"] = js["longitude"]
		locationInfo["timezone"]  = js["time_zone"]
		locationInfo["country"]   = js["country_name"]
		locationInfo["county"]    = js["region_name"]
		locationInfo["town"]      = js["city"]

	# get sun status. FYI : the 352 represents elevation which apparently needs to be hardcoded
	sunInfo = Location((locationInfo["town"],
                        locationInfo["country"],
                        locationInfo["latitude"],
                        locationInfo["longitude"],
                        locationInfo["timezone"], 
                            352)).sun()
	locationInfo["dawn"] = str(sunInfo["dawn"].time())
	locationInfo["dusk"] = str(sunInfo["dusk"].time())

	writeLocationFile()

def loadLocationFile():
	global locationInfo
	if Path(LOCATION_FILE).is_file():
		try:
			locationInfo = json.load(open(LOCATION_FILE))
			return True
		except Exception as e:
			print("Could not load location file json: %s" % str(e))
			return False
	else:
		print("No location file available")
		return False

def writeLocationFile():
	print("Trying to write location file")
	try:
		with open(LOCATION_FILE, 'w') as fp:
			json.dump(locationInfo, fp)
	except Exception as e:
		print("Could not write location file json: %s" % str(e))

def getDawnTime():
	return sunInfo['dawn'].time()

def getSunriseTime():
	return sunInfo['sunrise'].time()

def getSunsetTime(self):
	return sunInfo['sunset'].time()

def getDuskTime(self):
	return sunInfo['dusk'].time()

############ ZWAVE SPECIFIC PART ############

DIMMER_LEVEL_VAL = 72057594076299265
COLOR_VAL        = 72057594076512263
COLD_WHITE    = "#FFFFFF00FF"
WARM_WHITE    = "#FFFFFFFF00"
CURRENT_COLOR = ""

bulb_node = None

def startZwaveNetwork():
	options = ZWaveOption('/dev/ttyACM0', config_path='/home/pi/python-openzwave/openzwave/config', user_path='.', cmd_line='')
	options.set_append_log_file(True)
	options.set_console_output(False)
	options.set_save_log_level('Warning')
	options.set_logging(True)
	options.lock()

	network = ZWaveNetwork(options, log=None)

	#try for 10 seconds to wake the network up
	for i in range(0, 10):
		if network.state >= network.STATE_AWAKED:
			# network is awake, move on
			break;
		else:
			# network is still not awaken, let's wait a bit and then try again
			time.sleep(1.0)

	if network.state < network.STATE_AWAKED:
		print("WARNING: COULD NOT WAKE UP THE ZWAVE NETWORK")
		return
	for i in range(0, 10):
		if network.state >= network.STATE_READY:
			# network is ready for interacting
			break
		else:
			# network not yet ready, wait a bit and then try again
			time.sleep(1.0)

	if not network.is_ready:
		print("WARNING: NETWORK IS NOT READY FOR INTERACTING")
		return

	global bulb_node
	bulb_node = network.nodes[2]
	global CURRENT_COLOR
	CURRENT_COLOR = "#FFFFFF0000"
	setBulbColor(CURRENT_COLOR)
def setBulbColor(aValue):
	bulb_node.set_rgbw(COLOR_VAL, aValue)


def setBulbDimmer(aValue):
	if aValue == 100:
		aValue = 255
	bulb_node.set_dimmer(DIMMER_LEVEL_VAL, aValue)


######## MQTT SPECIFIC PART #########

mqtt_client = None

def mqtt_setBulbColor(aColor):
	setBulbColor(aColor)
	mqtt_client.publish("update_bulb_color", aColor)

def mqtt_setBulbIntensity(aIntensity):
	setBulbDimmer(aIntensity)

def mqtt_setColorTemp(aValue):
	if aValue == "cold":
		color = COLD_WHITE
	elif aValue == "warm":
		color = WARM_WHITE
	mqtt_setBulbColor(color)

def mqtt_update_info():
	locationData = json.dumps(locationInfo)
	mqtt_client.publish("info_update", locationData)

def mqtt_handleManualOverride(aValue):
	if aValue.lower() == 'false':
		mqtt_setBulbColor(CURRENT_COLOR)

def mqtt_setChangeTime(aValue):
	splitTime = aValue.split(":")
	global color_change_time
	color_change_time = datetime.time(hour=int(splitTime[0]),
	                                  minute=int(splitTime[1]),
	                                  second=0,
	                                  microsecond=0)
	print("Newly set time: %s" % str(color_change_time))
	
def on_msg_received(client, userdata, message):
	msg = str(message.payload.decode("UTF-8"))
	print("MQTT: Received : {}".format(msg))

	if message.topic == "set_bulb_color":
		mqtt_setBulbColor("#" + msg + "0000")
	elif message.topic == "bulb_intensity":
		mqtt_setBulbIntensity(int(msg))
	elif message.topic == "color_temp":
		mqtt_setColorTemp(msg)
	elif message.topic == "manual_override":
		print("manual override val %s" % msg)
		mqtt_handleManualOverride(msg)
	elif message.topic == "time_set":
		mqtt_setChangeTime(msg)

def setupCommunication():
	global mqtt_client
	mqtt_client = mqtt.Client("Flux_IO_client")
	mqtt_client.on_message=on_msg_received
	mqtt_client.connect("localhost")
	mqtt_client.loop_start()

	mqtt_client.subscribe("set_bulb_color")
	mqtt_client.subscribe("bulb_intensity")
	mqtt_client.subscribe("color_temp")
	mqtt_client.subscribe("manual_override")
	mqtt_client.subscribe("time_set")

###### Additionally needed functions ########
keepLooping = True

def signal_handler(signal, frame):
    global keepLooping
    print("Initializing graceful shutdown")
    mqtt_client.publish("stop", 0)
    mqtt_client.loop_stop()
    setBulbDimmer(0)
    keepLooping = False
    sys.exit(0)

####### The main part  ########

try :
	signal.signal(signal.SIGINT, signal_handler)
	print("Getting sun info")
	threading.Thread(target= printWaitingDots).start()
	getSunInformation()
	print("Sun info received");
	printDots = False
	print("Setting up ZWave network")
	threading.Thread(target= printWaitingDots).start()
	startZwaveNetwork()
	print("ZWave up and running")
	printDots = False
	print("Setting up MQTT communication")
	threading.Thread(target=printWaitingDots).start()
	setupCommunication()
	print("MQTT communication established")
	printDots = False
	print("Sending initial location info")
	mqtt_update_info()
	print("We're up and running")
	while keepLooping:
		time.sleep(0.1)

except Exception as e:
	printDots = False
	keepLooping = False
	if type(bulb_node) is ZWaveNode:
		setBulbDimmer(0)
	print("Main exception occurred: %s" % str(e))
