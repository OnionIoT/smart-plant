import time
from losantmqtt import Device

device = None

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

# initialize mqtt connection with losant
def init(deviceId, key, secret):
	global device

	# Construct device
	device = Device(deviceId, key, secret)

	# TODO: implement this for part 3
	# Listen for commands.
	#device.add_event_observer("command", on_command)

	# Connect to Losant.
	device.connect(blocking=False)

# send state measurement to Losant
def sendMeasurement(stateName, stateValue):
	device.loop()
	if device.is_connected():
		device.send_state({stateName: stateValue})
