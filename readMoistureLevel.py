import serial
import sys, os, getopt, time
from OmegaExpansion import oledExp

MEASUREMENT_COUNT 	= 15
OLED_EXP_PRESENT	= False

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
	print "                Set to %d by default"%(MEASUREMENT_COUNT)
	print ""

# read the command line arguments
try:
	opts, args = getopt.getopt(sys.argv[1:], "hn:o", ["help", "number=", "oled"])
except getopt.GetoptError:
	printUsage()
	sys.exit(2)
for opt, arg, in opts:
	if opt in ("-h", "--help"):
		printUsage()
		sys.exit()
	elif opt in ("-o", "--oled"):
		OLED_EXP_PRESENT = True
	elif opt in ("-n", "--number"):
		print "Setting measuremet count to ", arg
		try:
			MEASUREMENT_COUNT = int(arg)
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


# read analog value (0-1023) from the microcontroller
#	returns None if value is not read successfully
def readMoistureLevel():
	# need to write an 'r' character to trigger a measurement response
	serialPort.write('r')

	# read the response
	try:
		value = serialPort.readline()

		if value == "":
			print "Got blank value!"
			value = None
		else:
			value = value.rstrip() 	#chomp the newline at the end of the response
	except:
		value = None

	return value

# record the latest measurement, ensure the list of measurements is
# 	also performs error checking
def recordMeasurement(currentMeasurement, measurementList):
	# check input
	if currentMeasurement is None:
		return measurementList

	# convert the measurement string into an integer
	try:
		value = int(currentMeasurement)
	except:
		return measurementList

	# add it to the list
	measurementList.append(value)

	# remove the first element from the list
	if len(measurementList) > MEASUREMENT_COUNT:
		measurementList = measurementList[1:]

	return measurementList

# return the average of all of the measurements
def getAverageMeasurement(measurementList):
	# find the sum of all list elements
	sum = 0
	for val in measurementList:
		sum = sum + val

	# find the average
	average = int( sum / float(len(measurementList)) )

	return average

# initialze the OLED Expansion and set it up for use with the program
def oledInit(dirName):
	status  = oledExp.driverInit()
	if status != 0:
		print 'ERROR initializing OLED Expansion'

	## setup the display
	# draw the plant image to the screen
	imgFile = dirName + "/plant.oled"
	if os.path.exists(imgFile):
		status = oledExp.drawFromFile(imgFile)

	## write the default text
	# write the first word on the second line and the right side of the screen
	oledExp.setTextColumns()
	oledExp.setCursor(1,12)
	oledExp.write('Moisture')

	# write the second word on the third line and the right side of the screen
	oledExp.setTextColumns()
	oledExp.setCursor(2,12)
	oledExp.write('Level:')

def oledWriteMeasurements(average):
	# set the cursor the fifth line and the right side of the screen
	oledExp.setTextColumns()
	oledExp.setCursor(4,12)
	# write out the text
	oledExp.write( str(average) )

### MAIN PROGRAM ###
def mainProgram():
	# initialize the OLED Expansion
	if OLED_EXP_PRESENT:
		oledInit(dirName)

	# list to hold all measurements
	moistureLevels = []

	# program loop
	while True:
		# get the latest moisture sensor reading
		readValue = readMoistureLevel()
		print "> ", readValue
		# add the measurement to our list
		moistureLevels = recordMeasurement(readValue, moistureLevels)
		print "  ", moistureLevels
		# find the average value
		averageLevel = getAverageMeasurement(moistureLevels)
		print "  ", averageLevel

		# write the average measurement to the OLED
		if OLED_EXP_PRESENT:
			oledWriteMeasurements(averageLevel)

		time.sleep(1)

	# close the serial port
	serialPort.close()

if __name__ == "__main__":
	mainProgram()
