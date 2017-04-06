import serial
import sys, os, getopt, time

import measurementHelper
import oledHelper

MAX_MEASUREMENT_COUNT 	= 15
OLED_EXP_PRESENT		= False
VERBOSE					= False

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
	opts, args = getopt.getopt(sys.argv[1:], "hvn:o", ["help", "verbose", "number=", "oled"])
except getopt.GetoptError:
	printUsage()
	sys.exit(2)
for opt, arg, in opts:
	if opt in ("-h", "--help"):
		printUsage()
		sys.exit()
	elif opt in ("-v", "--verbose"):
		VERBOSE = True
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
serialPort = serial.Serial('/dev/ttyS1',9600,timeout=2)
if serialPort.isOpen() == False:
	print "ERROR: Failed to initialize serial port!"
	exit()



### MAIN PROGRAM ###
def mainProgram():
	# initialize the OLED Expansion
	if OLED_EXP_PRESENT:
		oledHelper.oledInit(dirName)

	# list to hold all measurements
	moistureLevels = []

	# program loop
	while True:
		# get the latest moisture sensor reading
		readValue = measurementHelper.readMoistureLevel(serialPort)
		if VERBOSE:
			print "> Latest measurement: ", readValue
		# add the measurement to our list
		moistureLevels = measurementHelper.recordMeasurement(readValue, moistureLevels, MAX_MEASUREMENT_COUNT)
		if VERBOSE:
			print " > Measurement List: ", moistureLevels
		# find the average value
		averageLevel = measurementHelper.getAverageMeasurement(moistureLevels)
		if VERBOSE:
			print " >> Average Value: ",
		print averageLevel

		# write the average measurement to the OLED
		if OLED_EXP_PRESENT:
			oledHelper.oledWriteMeasurements(averageLevel)

		time.sleep(1)

	# close the serial port
	serialPort.close()

if __name__ == "__main__":
	mainProgram()
