import os
from OmegaExpansion import oledExp

# initialze the OLED Expansion and set it up for use with the program
def oledInit(dirName):
	oledExp.setVerbosity(-1)
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

# write out the soil moisture value
def oledWriteMeasurements(average, percent):
	# set the cursor the fifth line and the right side of the screen
	oledExp.setTextColumns()
	oledExp.setCursor(4,12)
	# write out the text
	oledExp.write( str(average) )

	# set the cursor the sixth line and the right side of the screen
	oledExp.setTextColumns()
	oledExp.setCursor(5,12)
	# write out the text
	oledExp.write( str(percent) + "%" )
