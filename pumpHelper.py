import time
from OmegaExpansion import relayExp

RELAY_EXP_ADDR = 7
RELAY_EXP_CHANNEL = 0

PUMP_OFF = 0
PUMP_ON = 1


# if not already initialized, initialize the relay expansion
def _initRelayExpansion():
	# check if initialized
	bInit = relayExp.checkInit(RELAY_EXP_ADDR)

	if not bInit:
		# initialize the expansion
		status = relayExp.driverInit(RELAY_EXP_ADDR)
		if status != 0:
			print("ERROR: Could not initialize Relay Expansion!")
			return 1

	return 0

# return the state of the relay expansion channel that controls the pump
def _getPumpState():
	return( relayExp.readChannel(RELAY_EXP_ADDR, RELAY_EXP_CHANNEL) )

# set the relay expansion channel that controls the pump to a specified state
def _setPumpState(state):
	status = relayExp.setChannel(RELAY_EXP_ADDR, RELAY_EXP_CHANNEL, state)
	if status != 0:
		print("ERROR: could not set pump state!")
		return 1
	return 0

# turn the pump on for a speicified number of seconds
def activatePump(duration=1):
	# initialize the expansion
	status = _initRelayExpansion()

	# if pump is already on, ignore this command
	pumpState = _getPumpState()
	if pumpState == PUMP_ON:
		print("ERROR: pump already on")
		return 1

	# enable the pump
	status |= _setPumpState(PUMP_ON)
	# wait
	time.sleep(duration)
	# disable the pump
	status |= _setPumpState(PUMP_OFF)

	return status
