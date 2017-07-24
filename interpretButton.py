		
#
# Interpret Stand  Alone Button
#
#
import sys
import time

sys.path.append('./SDL_Pi_SSD1306')
sys.path.append('./Adafruit_Python_SSD1306')

import state
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import Adafruit_SSD1306

import Scroll_SSD1306

# define button debug

DEBUGBUT = False

def invertDisplay(display):
	display.command(Adafruit_SSD1306.SSD1306_INVERTDISPLAY)

def normalDisplay(display):
	display.command(Adafruit_SSD1306.SSD1306_NORMALDISPLAY)

def makeStatementDisplay(list, line,text):
	draw = list[1]	
	font = list[2]
	draw.text((0, 12*line),    text,  font=font, fill=255)

def startStatementDisplay(display):

	width = 128
	height = 64
	top = 0
	lineheight = 10
	currentLine = 0
	offset = 0
	
	image = Image.new('1', (width, height))
	draw = ImageDraw.Draw(image)
	# Load default font.
	font = ImageFont.load_default()
	display.clear()
	display.display()
	invertDisplay(display)
	return [image, draw, font]

def finishStatementDisplay(display, list):
	image = list[0]
	display.image(image)	
	display.display()
	time.sleep(2.0)
	display.clear()
	normalDisplay(display)

def deactivateAlarms():
	state.Alarm_Active = False
	buttonPush = False
	buttonState = 0

def interpretButton(display, OLEDLock, buttonState):  

		#############
		# Standalone Button Interface	
		#############
                if (DEBUGBUT):
                    print "Attempt OLEDLock acquired"
		OLEDLock.acquire()
                if (DEBUGBUT):
                    print "OLEDLock acquired"
		list = startStatementDisplay(display)
		# one button push = water now full
		if (buttonState == 1):
			makeStatementDisplay(list, 1,"    Water Filled" )
        		state.Pump_Water_Full = 1
            		state.Last_Event = "Water set to Full "+time.strftime("%Y-%m-%d %H:%M:%S")

		# two button push = set moisture threshold to current reading of moisture_sensor
		if (buttonState == 2):
			makeStatementDisplay(list, 1,"    Soil Moisture")
			makeStatementDisplay(list, 2,"      Threshold")
        		state.Moisture_Threshold =  state.Moisture_Humidity
			makeStatementDisplay(list, 3,"    Set to=%6.1f%%" % state.Moisture_Threshold)
            		state.Last_Event = ("Moisture Lim Set to %6.1f: " % state.Moisture_Threshold)+time.strftime("%Y-%m-%d %H:%M:%S")


		# three button push, set moisture threshold to default (65%)
		if (buttonState == 3):
			makeStatementDisplay(list, 1,"    Soil Moisture")
			makeStatementDisplay(list, 2,"      Threshold")
			makeStatementDisplay(list, 3,"  Set to default=65%") 
        		state.Moisture_Threshold = 65.0
            		state.Last_Event = ("Moisture Lim Set to %6.1f: " % state.Moisture_Threshold)+time.strftime("%Y-%m-%d %H:%M:%S")

		finishStatementDisplay(display,list)
                if (DEBUGBUT):
                    print "Attempt OLEDLock released"
		OLEDLock.release()
                if (DEBUGBUT):
                    print "OLEDLock released"
		buttonPush = False

