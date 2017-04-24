
MAX_MEASUREMENT_VALUE 		= 1023

# read analog value (0-1023) from the microcontroller
#	returns None if value is not read successfully
def readMoistureLevel(serialPort):
	# need to write an 'r' character to trigger a measurement response
	serialPort.write('r')

	# read the response
	try:
		value = serialPort.readline()

		if value == "":
			print("Got blank value!")
			value = None
		else:
			value = value.rstrip() 	#chomp the newline at the end of the response
	except:
		value = None

	return value

# record the latest measurement, ensure the list of measurements is
# 	also performs error checking
def recordMeasurement(currentMeasurement, measurementList, maxMeasurements):
	# check input
	if currentMeasurement is None:
		return measurementList

	# convert the measurement string into an integer
	try:
		value = int(currentMeasurement)
	except:
		return measurementList

	# convert the raw measurement into a percent
	percent = getMeasurementAsPercent(value)

	# add it to the list
	measurementList.append(percent)

	# remove the first element from the list
	if len(measurementList) > maxMeasurements:
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

# convert an analog microcntroller reading into a percentage
def getMeasurementAsPercent(measurement):
	percent = int( (float(measurement) / float(MAX_MEASUREMENT_VALUE)) * 100.0)
	return percent
