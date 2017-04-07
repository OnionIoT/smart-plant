import serial
import sys, os, getopt, time, signal

import measurementHelper
import oledHelper

MAX_MEASUREMENT_COUNT 	= 15
OLED_EXP_PRESENT		= False
VERBOSE					= True

# usage statement
def printUsage():
	print "Usage: smartPlant.py [-o] []"
	print ""
	print "Functionality:"
	print "    Collect soil moisture level and output the averaged value"
	print ""
	print "OPTIONS:"
	print "    -h          Show this message"
	print "    -o, --oled  Enable showing status on OLED Expansion"
	print "    -n R, --number R"
	print "                Where R is the number of measurements from"
	print "                which to calculate the average measurement value."
	print "                Set to %d by default"%(MAX_MEASUREMENT_COUNT)
	print ""

# read the command line arguments
try:
	opts, args = getopt.getopt(sys.argv[1:], "hvqn:o", ["help", "verbose", "quiet", "number=", "oled"])
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
	elif opt in ("-n", "--number"):
		print "Setting measuremet count to ", arg
		try:
			MAX_MEASUREMENT_COUNT = int(arg)
		except:
			print("ERROR: invalid input")
			printUsage()
			sys.exit()

# find the directory of the script
dirName = os.path.dirname(os.path.abspath(__file__))

# initialize the serial port
serialPort = serial.Serial('/dev/ttyS1', 9600, timeout=2)
if serialPort.isOpen() == False:
	print "ERROR: Failed to initialize serial port!"
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
		print "> Latest measurement: ", readValue

	# add the measurement to our list
	measurementList = measurementHelper.recordMeasurement(readValue, measurementList, MAX_MEASUREMENT_COUNT)
	if VERBOSE:
		print " > Measurement List: ",
		for val in measurementList:
			print "%d%% "%(val),
		print ""

	# find the average value
	averageLevel = measurementHelper.getAverageMeasurement(measurementList)
	if VERBOSE:
		print " >> Average Value: %d%%"%(averageLevel)
	else:
		print averageLevel

	# write the average measurement to the OLED
	if OLED_EXP_PRESENT:
		oledHelper.writeMeasurements(averageLevel)

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
