import time
from losantmqtt import Device

device = None
waterPlantFunction = None

# check if config file has: deviceId, key, and secret
#	if it does, return True
# 	if not, return False
def isConfigValid(config):
	bValid = False
	if 'deviceId' in config:
		bValid = True
	if 'key' in config:
		bValid = True
	if 'secret' in config:
		bValid = True

	if not bValid:
		print("ERROR: Losant config file must contain:")
		print("   deviceId")
		print("   key")
		print("   secret")

	return bValid

# carry out actions from received commands
def onCommand(device, command):
	print("> Losant command!")
	if command["name"] == "waterPlant":
		print(" > Watering plant!")
		try:
			duration = int(command["payload"])
			waterPlantFunction(duration)
		except:
			waterPlantFunction()

# initialize mqtt connection with losant
def init(deviceId, key, secret, waterPlantFunctionPtr=None):
	global device
	# Construct device
	device = Device(deviceId, key, secret)

	# setup command functions
	global waterPlantFunction
	waterPlantFunction = waterPlantFunctionPtr
	# Listen for commands
	device.add_event_observer("command", onCommand)

	# Connect to Losant.
	device.connect(blocking=False)

# send state measurement to Losant
def sendMeasurement(stateName, stateValue):
	device.loop()
	if device.is_connected():
		device.send_state({stateName: stateValue})
