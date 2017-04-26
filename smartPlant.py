import serial
import sys, os, getopt, time, signal, json

import measurementHelper
import oledHelper

VERBOSE	= True
MAX_MEASUREMENT_COUNT = 15
OLED_EXP_PRESENT = False
LOSANT_CLOUD = False
PUMP_PRESENT = False
losantConfig = {}

# find the directory of the script
dirName = os.path.dirname(os.path.abspath(__file__))

# usage statement
def printUsage():
	print("Usage: smartPlant.py [-o] []")
	print ("")
	print("Functionality:")
	print("    Collect soil moisture level and output the averaged value")
	print("")
	print("OPTIONS:")
	print("    -h          Show this message")
	print("    -o, --oled  Enable showing status on OLED Expansion")
	print("    -n R, --number R")
	print("                Where R is the number of measurements from")
	print("                which to calculate the average measurement value.")
	print("                Set to %d by default"%(MAX_MEASUREMENT_COUNT))
	print("    -l <json file>, --losant <json file>")
	print("                Enable connection and reporting of plant data to Losant.")
	print("                Where <json file> is a path to a JSON configuration file ")
	print("                that must contain: the Losant deviceId, key, and secret")
	print("    -p, --pump  Enable receiving command from Losant to enable")
	print("                a water pump for a specified duration")
	print("")

# read the command line arguments
try:
	opts, args = getopt.getopt(sys.argv[1:], "hvqn:ol:p", ["help", "verbose", "quiet", "number=", "oled", "losant=", "pump"])
except getopt.GetoptError:
	printUsage()
	sys.exit(2)
for opt, arg, in opts:
	if opt in ("-h", "--help"):
		printUsage()
		sys.exit()
	elif opt in ("-v", "--verbose"):
		VERBOSE = True
	elif opt in ("-q", "--quiet"):
		VERBOSE = False
	elif opt in ("-o", "--oled"):
		OLED_EXP_PRESENT = True
	elif opt in ("-l", "--losant"):
		import losantHelper
		LOSANT_CLOUD = True
		filepath = '/'.join([dirName, arg])
		if os.path.abspath(arg):
			filepath = arg
		with open( filepath ) as f:
			try:
				losantConfig = json.load(f)
			except:
				print("ERROR: expecting JSON file")
				sys.exit()
			if not losantHelper.isConfigValid(losantConfig):
				sys.exit()
	elif opt in ("-p", "--pump"):
		import pumpHelper
		PUMP_PRESENT = True
	elif opt in ("-n", "--number"):
		print("Setting measuremet count to %s"%(arg))
		try:
			MAX_MEASUREMENT_COUNT = int(arg)
		except:
			print("ERROR: invalid input")
			printUsage()
			sys.exit()

# initialize the serial port
serialPort = serial.Serial('/dev/ttyS1', 9600, timeout=2)
if serialPort.isOpen() == False:
	print("ERROR: Failed to initialize serial port!")
	exit()

# function to close the serial port
def closePort():
	if serialPort.isOpen():
		serialPort.close()


# get a reading from the plant, average it out with previous readings and display it on the command line and optionally on the OLED
def getPlantMeasurement(measurementList):
	# get the latest moisture sensor reading
	readValue = measurementHelper.readMoistureLevel(serialPort)
	if VERBOSE:
		print("> Latest measurement: %s"%(readValue))

	# add the measurement to our list
	measurementList = measurementHelper.recordMeasurement(readValue, measurementList, MAX_MEASUREMENT_COUNT)
	if VERBOSE:
		print(" > Measurement List: "),
		for val in measurementList:
			print ("%d%% "%(val)),
		print("")

	# find the average value
	averageLevel = measurementHelper.getAverageMeasurement(measurementList)
	if VERBOSE:
		print(" >> Average Value: %d%%"%(averageLevel))
	else:
		print(averageLevel)

	# write the average measurement to the OLED
	if OLED_EXP_PRESENT:
		oledHelper.writeMeasurements(averageLevel)

	# send average measurement to Losant Cloud
	if LOSANT_CLOUD:
		losantHelper.sendMeasurement("moisture", averageLevel)
		if VERBOSE:
			print(" > sent value to Losant")
	return measurementList

# function to run before ending the program
def endMeasurements():
	if OLED_EXP_PRESENT:
		oledHelper.setDoneScreen()
	closePort()


# Signal interrupt handler
def signalHandler(signal, frame):
	endMeasurements()
	sys.exit()

# define a signal to run a function when ctrl+c is pressed
signal.signal(signal.SIGINT, signalHandler)



### MAIN PROGRAM ###
def mainProgram():
	# initialize the OLED Expansion
	if OLED_EXP_PRESENT:
		oledHelper.init(dirName)

	# setup the pump function
	pumpFunction = None
	if PUMP_PRESENT:
		pumpFunction = pumpHelper.activatePump

	# initialize connection to Losant Cloud
	if LOSANT_CLOUD:
		losantHelper.init(losantConfig['deviceId'], losantConfig['key'], losantConfig['secret'], pumpFunction)

	# list to hold all measurements
	moistureLevels = []

	# program loop
	while True:
		# get a reading from the plant
		moistureLevels = getPlantMeasurement(moistureLevels)
		# delay between readings
		time.sleep(1)

	# close the serial port
	endMeasurements()

if __name__ == "__main__":
	mainProgram()
