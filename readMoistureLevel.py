import serial
import time

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
	#time.sleep(0.001)
	#serialPort.reset_input_buffer() # needed so the program doesn't hang while trying to send new bytes

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


### MAIN PROGRAM ###
def mainProgram():
	while True:
		readValue = readMoistureLevel()
		print "> ", readValue
		time.sleep(1)

	serialPort.close()

if __name__ == "__main__":
	mainProgram()
