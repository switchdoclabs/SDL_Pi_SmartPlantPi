#!/usr/bin/env python
#
#
# SmartPlantPi 
#
# SwitchDoc Labs, Initial:  November 2016
#

SMARTPLANTPIVERSION = "017"
#imports 

import sys
import os
import RPi.GPIO as GPIO
import time
import threading
import json
import pickle

from pubnub.pubnub import PubNub
from pubnub.pubnub import PNConfiguration


#appends
sys.path.append('./SDL_Pi_HDC1000')
sys.path.append('./SDL_Pi_SSD1306')
sys.path.append('./Adafruit_Python_SSD1306')
sys.path.append('./SDL_Pi_SI1145')
sys.path.append('./SDL_Pi_RotaryButton')
sys.path.append('./SDL_Pi_Grove4Ch16BitADC/SDL_Adafruit_ADS1x15')

import interpretButton
import interpretRotary

import SDL_Pi_HDC1000
import SDL_Pi_RotaryButton

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import Adafruit_SSD1306

import Scroll_SSD1306

import SDL_Pi_SI1145
import SI1145Lux

from SDL_Adafruit_ADS1x15 import ADS1x15

import AirQualitySensorLibrary 

from datetime import datetime
from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler

import apscheduler.events

# Check for user imports
try:
            import conflocal as config
except ImportError:
            import config

if (config.enable_MySQL_Logging == True):
            import MySQLdb as mdb

import state


#############
# Debug True or False
############

DEBUG = False

#initialization

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

################
# Update State Lock - keeps smapling from being interrupted (like by checkAndWater)
################
UpdateStateLock = threading.Lock()



###############
# Optional LED
###############

def blinkLED(times, length):

	GPIO.setup(config.ledGPIO,GPIO.OUT)
	GPIO.output(config.ledGPIO, GPIO.LOW)
	for x in range(0,times):
		GPIO.output(config.ledGPIO, GPIO.HIGH)
		time.sleep(length)
		GPIO.output(config.ledGPIO, GPIO.LOW)

###############
#flow sensor
###############
GPIO.setup(config.FlowSensorPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  
NbTopsFan = 0
	 

# handle the flow sensor event
def flowSensorEventHandler (pin):
    #print "handling flow Sensor event"
    global NbTopsFan

    NbTopsFan = NbTopsFan +1

###############
# button sensor setup
###############
GPIO.setup(config.buttonClick, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  

# handle the button click event
def buttonClickEventHandler (pin):
    global buttonPush, buttonInProgress, buttonState, buttonStartTime, scheduler
    if (DEBUG):
    	print "handling button Click event. preBS=",buttonState
    if (buttonPush == False):
    	if (buttonInProgress == False):
		buttonInProgress = True
		buttonPush = False
		buttonState = 1
		buttonStartTime = time.time()
    		endTime = datetime.now() + timedelta(seconds=2)
		scheduler.add_job(buttonSampleEnd, 'date', run_date=endTime)
        	#state.SPP_State =state.SPP_States.Button
                #publishStatusToPubNub()
		return
    	else:
		buttonState = buttonState +1
		# limit to 3
		if (buttonState > 3):
			buttonState = 3
		return
		

def buttonSampleEnd():
    	global buttonPush, buttonInProgress, buttonState, buttonStartTime 

	buttonInProgress = False
	buttonPush = True
        publishStatusToPubNub()
        #state.SPP_State =state.SPP_States.Monitor
	#print "button Sample End back to Monitor"




buttonPush = False
buttonInProgress = False
buttonState = 0
buttonStartTime =  0

###############
#rotary dial and button init
###############
rotary = SDL_Pi_RotaryButton.SDL_Pi_RotaryButton()

    
###############
# pump setup
###############
GPIO.setup(config.USBEnable, GPIO.OUT)
GPIO.setup(config.USBControl, GPIO.OUT)
GPIO.output(config.USBEnable, GPIO.LOW)

def startPump():
        blinkLED(1,0.5)
        GPIO.output(config.USBEnable, GPIO.LOW)
        GPIO.output(config.USBControl, GPIO.HIGH)

def stopPump():
        blinkLED(1,0.5)
        GPIO.output(config.USBEnable, GPIO.HIGH)
        GPIO.output(config.USBControl, GPIO.LOW)

def pumpWater(timeInSeconds):
    global NbTopsFan
    if (timeInSeconds <= 0.0):
        return 0.0
    totalWaterPumped = 0
    startPump()
    i = timeInSeconds 
    while (i > 0.0):
	    NbTopsFan = 0   #Set NbTops to 0 ready for calculations
  	    time.sleep(1);   #Wait 1 second
  	    Calc = 60.0*(NbTopsFan * 60.0/ 73.0); #Pulse frequency x 60) / 73Q, = flow rate in L/hour 
    	    if (DEBUG):
  	    	print " L/hour %6.2f L/second=%6.2f" % (Calc, (NbTopsFan/73.0))
            i = i -1.0    
            totalWaterPumped = totalWaterPumped + (NbTopsFan / 73.0) 
    stopPump()

    return totalWaterPumped

def waterPlant():
            # We want to put off this state if Update State is .is locked.   That will prevent Update State from being hosed by this state machine
            if (DEBUG):
                  print "WP-Attempt UpdateStateLock acquired"
	    UpdateStateLock.acquire()
            if (DEBUG):
                  print "WP-UpdateStateLock acquired"



            previousState = state.SPP_State;
	    #if(state.SPP_State == state.SPP_States.Monitor):
            state.SPP_State =state.SPP_States.Watering
            publishStatusToPubNub()
            totalWaterPumped =  pumpWater(2.0)
           
            if (totalWaterPumped <= 0.0):
                state.Pump_Water_Full = False
            else:
                state.Pump_Water_Full = True

	    if (DEBUG):
		print "Total Water Pumped = %6.2f" % totalWaterPumped 
            state.SPP_State = previousState
            publishStatusToPubNub()
            state.Last_Event = "Plant Watered at: "+time.strftime("%Y-%m-%d %H:%M:%S")
            if (DEBUG):
                  print "WP-Attempt UpdateStateLock released"
            UpdateStateLock.release()
            if (DEBUG):
                  print "WP-UpdateStateLock released"

###############
# Sunlight SI1145 Sensor Setup
################


Sunlight_Sensor = SDL_Pi_SI1145.SDL_Pi_SI1145()
time.sleep(1)

try:
        state.Sunlight_Visible = SI1145Lux.SI1145_VIS_to_Lux(Sunlight_Sensor.readVisible())

        config.Sunlight_Present = True
except:
        config.Sunlight_Present = False

################
#SSD 1306 setup
################

# OLED SSD_1306 Detection

try:
        RST =27
        display = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)
        # Initialize library.
        display.begin()
        display.clear()
        display.display()
        config.OLED_Present = True
	OLEDLock = threading.Lock()
except:
        config.OLED_Present = False

################
#4 Channel ADC ADS1115 setup
################
# Set this to ADS1015 or ADS1115 depending on the ADC you are using!
ADS1115 = 0x01  # 16-bit ADC

ads1115 = ADS1x15(ic=ADS1115, address=0x48)

# Select the gain
gain = 6144  # +/- 6.144V
#gain = 4096  # +/- 4.096V

# Select the sample rate
sps = 250  # 250 samples per second
# determine if device present
try:
       value = ads1115.readRaw(0, gain, sps) # AIN0 wired to AirQuality Sensor
       time.sleep(1.0)
       value = ads1115.readRaw(0, gain, sps) # AIN0 wired to AirQuality Sensor

       config.ADS1115_Present = True

except TypeError as e:
       config.ADS1115_Present = False

################
# HDC1000 Setup
################
config.HDC1000_Present = False
try:

    hdc1000 = SDL_Pi_HDC1000.SDL_Pi_HDC1000()
    config.hdc1000_Present = True

except:
    config.hdc1000_Present = False



################
# Unit Conversion
################
# 

def returnTemperatureCF(temperature):
	if (state.EnglishMetric == True):
		# return Metric 
		return temperature
	else:
		return (9.0/5.0)*temperature + 32.0

def returnTemperatureCFUnit():
	if (state.EnglishMetric == True):
		# return Metric 
		return "C"
	else:
		return  "F"


################
#Pubnub configuration 
################
# 

pnconf = PNConfiguration()
 
pnconf.subscribe_key = config.Pubnub_Subscribe_Key
pnconf.publish_key = config.Pubnub_Publish_Key
  

pubnub = PubNub(pnconf)

def publish_callback(result, status):
        if (DEBUG):
		print "status.is_error", status.is_error()
		print "status.original_response", status.original_response
		pass
        # handle publish result, status always present, result if successful
        # status.isError to see if error happened

def publishStatusToPubNub():

        myMessage = {}
        myMessage["SmartPlantPi_CurrentStatus"] = state.SPP_Values[state.SPP_State]
        
        if (DEBUG):
        	print myMessage

        pubnub.publish().channel('SmartPlantPi_Data').message(myMessage).async(publish_callback)

def publishEventToPubNub():

        myMessage = {}
        myMessage["SmartPlantPi_Last_Event"] = state.Last_Event
        
        if (DEBUG):
        	print myMessage

        pubnub.publish().channel('SmartPlantPi_Data').message(myMessage).async(publish_callback)

def publishAlarmToPubNub(alarmText):

        myMessage = {}
        myMessage["SmartPlantPi_Alarm"] = alarmText 
        
        if (DEBUG):
        	print myMessage

        pubnub.publish().channel('SmartPlantPi_Data').message(myMessage).async(publish_callback)

def publishStateToPubNub():
	
        if (DEBUG):
        	print('Publishing Data to PubNub time: %s' % datetime.now())


        myMessage = {}
        myMessage["SmartPlantPi_Visible"] = "{:4.2f}".format(state.Sunlight_Vis) 
        myMessage["SmartPlantPi_IR"] = "{:4.2f}".format(state.Sunlight_IR) 
        myMessage["SmartPlantPi_UVIndex"] = "{:4.2f}".format(state.Sunlight_UVIndex) 
        myMessage["SmartPlantPi_MoistureHumidity"] = "{:4.1f}".format(state.Moisture_Humidity) 
        myMessage["SmartPlantPi_AirQuality_Sensor_Value"] = "{}".format(state.AirQuality_Sensor_Value) 
        myMessage["SmartPlantPi_AirQuality_Sensor_Number"] = "{}".format(state.AirQuality_Sensor_Number) 
        myMessage["SmartPlantPi_AirQuality_Sensor_Text"] = "{}".format(state.AirQuality_Sensor_Text) 
        myMessage["SmartPlantPi_Temperature"] = "{:4.1f} {}".format(returnTemperatureCF(state.Temperature), returnTemperatureCFUnit() )
        myMessage["SmartPlantPi_Humidity"] = "{:4.1f}".format(state.Humidity) 
        myMessage["SmartPlantPi_CurrentStatus"] = "{}".format(state.SPP_Values[state.SPP_State])
        myMessage["SmartPlantPi_Moisture_Threshold"] = '{:4.1f}'.format(state.Moisture_Threshold)
        myMessage["SmartPlantPi_Version"] = '{}'.format(SMARTPLANTPIVERSION) 
        myMessage["SmartPlantPi_Last_Event"] = "{}".format(state.Last_Event)
        if (state.Pump_Water_Full == 0): 
            myMessage["SmartPlantPi_Water_Full_Text"] = "{}".format("Empty" )
            myMessage["SmartPlantPi_Water_Full_Direction"] = "{}".format("180" )
        else:
            myMessage["SmartPlantPi_Water_Full_Text"] = "{}".format("Full" )
            myMessage["SmartPlantPi_Water_Full_Direction"] = "{}".format("0" )

        if (DEBUG):
        	print myMessage

        pubnub.publish().channel('SmartPlantPi_Data').message(myMessage).async(publish_callback)

        blinkLED(3,0.200)


#############################
# apscheduler setup
#############################
# setup tasks
#############################

def tick():
    print('Tick! The time is: %s' % datetime.now())


def killLogger():
    scheduler.shutdown()
    print "Scheduler Shutdown...."
    exit()


def checkAndWater():


    print "checkandWater: %0.2f Threshold / %0.2f Current" % (state.Moisture_Threshold, state.Moisture_Humidity)
    if (state.Moisture_Humidity <= state.Alarm_Moisture_Sensor_Fault):
	    print "No Watering - Moisture Sensor Fault Detected!"		
    else:
    	    if (state.Moisture_Threshold > state.Moisture_Humidity):
	    	print "Watering Plant"
            	waterPlant();
            



def ap_my_listener(event):
        if event.exception:
              print event.exception
              print event.traceback


def returnStatusLine(device, state):

        returnString = device
        if (state == True):
                returnString = returnString + ":   \t\tPresent"
        else:
                returnString = returnString + ":   \t\tNot Present"
        return returnString


#############################
# get and store sensor state
#############################

def outputStateToJSON():


    if (config.AlexaSupport == True):
        try:
            with open('/var/www/html/SmartPlantState.json', 'w') as outfile:
                json.dump(
                      {"Temperature": '{0:0.1f} deg {1}'.format(returnTemperatureCF(state.Temperature),returnTemperatureCFUnit()),
                      "Humidity": '{0:0.1f} %'.format(state.Humidity), 
                      "Sunlight_Vis": '{0:0.1f} lux'.format(state.Sunlight_Vis), 
                      "Sunlight_IR": '{0:0.1f} lux'.format(state.Sunlight_IR), 
                      "Sunlight_UVIndex": '{0:0.1f}'.format(state.Sunlight_UVIndex), 
                      "Moisture_Humidity": '{0:0.1f} %'.format(state.Moisture_Humidity), 
                      "Pump_Water_Full": '{}'.format(state.Pump_Water_Full), 
                      "AirQuality_Sensor_Text":'{}'.format(state.AirQuality_Sensor_Text), 
                      "AirQuality_Sensor_Number":'{}'.format(state.AirQuality_Sensor_Number), 
                      "Moisture_Threshold":'{0:0.1f}'.format(state.Moisture_Threshold), 
                      "SamrtPlantPi_Version":'{}'.format(SMARTPLANTPIVERSION), 
                      "Sample_Timestamp":'{}'.format(time.strftime("%H:%M %d-%m-%Y "))}, 
                      outfile)
        except:
            pass

def saveState():
	    output = open('SPPState.pkl', 'wb')

	    # Pickle dictionary using protocol 0.
	    pickle.dump(state.Moisture_Threshold, output)
	    pickle.dump(state.EnglishMetric, output)
	    pickle.dump(state.Alarm_Temperature, output)
	    pickle.dump(state.Alarm_Moisture, output)
	    pickle.dump(state.Alarm_Water, output)
	    pickle.dump(state.Alarm_Air_Quality, output)
	    pickle.dump(state.Alarm_Active, output)

	    output.close()

############
# Setup Moisture Pin for GrovePowerSave
############
GPIO.setup(config.moisturePower,GPIO.OUT)
GPIO.output(config.moisturePower, GPIO.LOW)

def readMoistureValue():
	if (config.ADS1115_Present):
                GPIO.output(config.moisturePower, GPIO.HIGH)
       		Moisture_Raw   = ads1115.readADCSingleEnded(config.moistureADPin, gain, sps)/7 # AIN0 wired to AirQuality Sensor
                GPIO.output(config.moisturePower, GPIO.LOW)

       		Moisture_Humidity   = Moisture_Raw/7 
       		if (DEBUG):
               		print "Pre Limit Moisture_Humidity=", Moisture_Humidity
       		if (Moisture_Humidity >100): 
       		 	Moisture_Humidity = 100;
       		if (Moisture_Humidity <0): 
                 	Moisture_Humidity = 0;
                    
       		if (DEBUG):
               		print "Moisture Humidity = %0.2f" % (Moisture_Humidity)
       		if (DEBUG):
              		print"------------------------------"
	else:
		Moisture_Humidity = 0.0

	return Moisture_Humidity

def updateState():

  if (DEBUG):
      print "Attempt UpdateStateLock acquired"
  UpdateStateLock.acquire()
  if (DEBUG):
      print "UpdateStateLock acquired"


  # catch Exceptions and MAKE SURE THE LOCK is released!
  try:
    if (state.SPP_State == state.SPP_States.Monitor):  
            state.SPP_State =state.SPP_States.Sampling
            publishStatusToPubNub()
	    if (DEBUG):
            	print "----------------- "
            	print "Update State"
            	print "----------------- "
            if (config.Sunlight_Present == True):
        			if (DEBUG):
                                	print " Sunlight Vi/state.Sunlight_IR/UV Sensor"
            else:
        			if (DEBUG):
                                	print " Sunlight Vi/state.Sunlight_IR/UV Sensor Not Present"
            if (DEBUG):
            	print "----------------- "
    
            if (config.Sunlight_Present == True):
                    ################
                    state.Sunlight_Vis = SI1145Lux.SI1145_VIS_to_Lux(Sunlight_Sensor.readVisible())
                    state.Sunlight_IR = SI1145Lux.SI1145_IR_to_Lux(Sunlight_Sensor.readIR())
                    state.Sunlight_UV = Sunlight_Sensor.readUV()
                    state.Sunlight_UVIndex = state.Sunlight_UV / 100.0

            	    if (DEBUG):
                    	print 'Sunlight Visible:  ' + str(state.Sunlight_Vis)
                    	print 'Sunlight state.Sunlight_IR:       ' + str(state.Sunlight_IR)
                    	print 'Sunlight UV Index (RAW): ' + str(state.Sunlight_UV)
                    	print 'Sunlight UV Index: ' + str(state.Sunlight_UVIndex)
                    ################
    
    
            if (config.ADS1115_Present):
                state.Moisture_Humidity  = readMoistureValue() 
    
                state.AirQuality_Sensor_Value =  AirQualitySensorLibrary.readAirQualitySensor(ads1115)
    
                sensorList = AirQualitySensorLibrary.interpretAirQualitySensor(state.AirQuality_Sensor_Value)
            	if (DEBUG):
                	print "Sensor Value=%i --> %s  | %i"% (state.AirQuality_Sensor_Value, sensorList[0], sensorList[1])

                state.AirQuality_Sensor_Number = sensorList[1] 
                state.AirQuality_Sensor_Text = sensorList[0] 
                 
            # read temp humidity
   
            if (config.hdc1000_Present):
                state.Temperature= hdc1000.readTemperature()
                state.Humidity = hdc1000.readHumidity()
    
           	if (DEBUG):
            		print 'Temp             = {0:0.3f} deg C'.format(state.Temperature)
            		print 'Humidity         = {0:0.2f} %'.format(state.Humidity)
    
            state.SPP_State =state.SPP_States.Monitor
            publishStatusToPubNub()
        
            outputStateToJSON()

            if (config.OLED_Present) and (state.SPP_State == state.SPP_States.Monitor) :


                    if (DEBUG):
                          print "Attempt OLEDLock acquired"
		    OLEDLock.acquire()
                    if (DEBUG):
                          print "OLEDLock acquired"
                    Scroll_SSD1306.addLineOLED(display,  ("----------"))
                    Scroll_SSD1306.addLineOLED(display,  ("Plant Moisture = \t%0.2f %%")%(state.Moisture_Humidity))
                    Scroll_SSD1306.addLineOLED(display,  ("Temperature = \t%0.2f %s")%(returnTemperatureCF(state.Temperature), returnTemperatureCFUnit()))
                    Scroll_SSD1306.addLineOLED(display,  ("Humidity =\t%0.2f %%")%(state.Humidity))
                    Scroll_SSD1306.addLineOLED(display,  ("Air Qual = %d/%s")%(state.AirQuality_Sensor_Value, state.AirQuality_Sensor_Text))
                    Scroll_SSD1306.addLineOLED(display,  ("Sunlight = \t%0.2f Lux")%(state.Sunlight_Vis))
                    if (DEBUG):
                        print "Attempt OLEDLock released"
		    OLEDLock.release()
                    if (DEBUG):
 
                        print "OLEDLock released"
 
  except:
    if (DEBUG):
        print "Exception Raised in Update State"
  finally:
 
    if (DEBUG):
          print "Attempt UpdateStateLock released"
    UpdateStateLock.release()
    if (DEBUG):
          print "UpdateStateLock released"


#############################
# Alarm Displays 
#############################
def checkForAlarms():

	# check to see alarm
        if (DEBUG):
		print "checking for alarm"

	if (state.Alarm_Active == True):
		activeAlarm = False
        	if (DEBUG):
			print "state.Alarm_Air_Quality=", state.Alarm_Air_Quality
			print "state.AirQuality_Sensor_Value", state.AirQuality_Sensor_Value

		if (state.Alarm_Temperature >= state.Temperature):
        		if (DEBUG):
				print "---->Low Temperature Alarm!"
			activeAlarm = True

		if (state.Alarm_Moisture >= state.Moisture_Humidity):
        		if (DEBUG):
				print "---->Moisture Alarm!"
			activeAlarm = True

		if (state.Alarm_Water  == True ):
			if (state.Pump_Water_Full == False):
        			if (DEBUG):
					print "---->Water Empty Alarm!"
				activeAlarm = True
		
		if (state.Alarm_Air_Quality <  state.AirQuality_Sensor_Value):
        			if (DEBUG):
					print "---->Air Quality Alarm!"
				activeAlarm = True

        	if (DEBUG):
			print "activeAlarm = ", activeAlarm		
		if (activeAlarm == True):
			displayActiveAlarms()
		else:
			publishAlarmToPubNub("")


def centerText(text,sizeofline):
        textlength = len(text)
        spacesCount = (sizeofline - textlength)/2
        mytext = ""
        if (spacesCount > 0):
                for x in range (0, spacesCount):
                        mytext = mytext + " "
        return mytext+text
	
def startAlarmStatementDisplay(display):

        width = 128
        height = 64
        top = 0
        lineheight = 10
        currentLine = 0
        offset = 0

        image = Image.new('1', (width, height))
        draw = ImageDraw.Draw(image)
        # Load font.
        font = ImageFont.truetype('/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf', 12)
        display.clear()
        display.display()
        return [image, draw, font, display]

def displayAlarmStatementOLEDDisplay(list, text,lengthofline=18):

        image = list[0]
        draw = list[1]
        font = list[2]
        display = list[3]

        font = ImageFont.truetype('/usr/share/fonts/truetype/roboto/Roboto-BoldItalic.ttf', 25)
        draw.rectangle((0,0,127,5*12+2), outline=0, fill=255)
        draw.text((0, 1*12),    centerText(text, lengthofline),  font=font, fill=0)


        display.image(image)
        display.display()

        return [image, draw, font, display]

def displayAlarmOLEDDisplay(list, text, lengthofline=18):

        image = list[0]
        draw = list[1]
        font = list[2]
        display = list[3]

        font = ImageFont.truetype('/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf', 25)
        draw.rectangle((0,0,127,5*12+2), outline=0, fill=0)
        draw.text((0, 2*12-4),    centerText(text, lengthofline),  font=font, fill=255)


        display.image(image)
        display.display()

        return [image, draw, font, display]


def finishAlarmStatementDisplay(list):
        image = list[0]
        display = list[3]
        display.clear()
        display.display()


def displayActiveAlarms():

	# display Alarm
        if (DEBUG):
		print "Display Alarms"
    	if ((config.OLED_Present == True) and (state.SPP_State == state.SPP_States.Monitor)):

                if (DEBUG):
                      print "Attempt OLEDLock acquired"
        	OLEDLock.acquire()
                if (DEBUG):
                      print "OLEDLock acquired"
		
        	state.SPP_State =state.SPP_States.Alarm
                publishStatusToPubNub()
		# initialize 
		list = startAlarmStatementDisplay(display)
		# Flash white screen w/Alarm in middle
		displayAlarmStatementOLEDDisplay(list, "ALARM!",lengthofline=13)
		time.sleep(2.0)
		# wait 2 seconds
		finishAlarmStatementDisplay(list)

		# display alarms, one per screen on black screen
		list = startAlarmStatementDisplay(display)


    		
    		if (state.Moisture_Humidity <= state.Alarm_Moisture_Sensor_Fault):
        		if (DEBUG):
				print "---->Moisture Sensor Fault"
			displayAlarmOLEDDisplay(list, "MS Fault!", 10)
			publishAlarmToPubNub("Mois Sen Fault")
			time.sleep(1.0)

		if (state.Alarm_Temperature >= state.Temperature):
        		if (DEBUG):
				print "---->Temperature Alarm!"
			displayAlarmOLEDDisplay(list, "Low Temp", 10)
			publishAlarmToPubNub("Low Temp")
			time.sleep(1.0)

		if (state.Alarm_Moisture >= state.Moisture_Humidity):
			displayAlarmOLEDDisplay(list, "Plant Dry", 14)
			publishAlarmToPubNub("Plant Dry")
			time.sleep(1.0)

		if (state.Alarm_Water  == True ):
			if (state.Pump_Water_Full == False):
				displayAlarmOLEDDisplay(list, "No Water", 12)
				publishAlarmToPubNub("No Water")
				time.sleep(1.0)

		if (state.Alarm_Air_Quality <  state.AirQuality_Sensor_Value):
			displayAlarmOLEDDisplay(list, "Air Quality", 14)
			publishAlarmToPubNub("Air Quality")
			time.sleep(1.0)


		finishAlarmStatementDisplay(list)
		publishAlarmToPubNub("Alarms!")

		# Flash white to end
		list = startAlarmStatementDisplay(display)
		# Flash white screen w/Alarm in middle
		displayAlarmStatementOLEDDisplay(list, "ALARM!",lengthofline=15)
		time.sleep(1.0)
		# wait 1 seconds
		finishAlarmStatementDisplay(list)

        	state.SPP_State = state.SPP_States.Monitor
                publishStatusToPubNub()

                if (DEBUG):
                    print "Attempt OLEDLock released"
        	OLEDLock.release()
                if (DEBUG):
                    print "OLEDLock released"

		if (state.Alarm_Active == False):   # it has been disabled
			publishAlarmToPubNub("deactivated")
		# do an updateState so screen looks more responsive
		scheduler.add_job(updateState )
#############################
# main program
#############################


# Main Program
if __name__ == '__main__':

    print ""
    print "SmartPlant Pi Version "+SMARTPLANTPIVERSION+"  - SwitchDoc Labs"
    print ""
    print "Program Started at:"+ time.strftime("%Y-%m-%d %H:%M:%S")
    print ""

    
    print returnStatusLine("ADS1115",config.ADS1115_Present)
    print returnStatusLine("OLED",config.OLED_Present)
    print returnStatusLine("Sunlight Sensor",config.Sunlight_Present)
    print returnStatusLine("hdc1000 Sensor",config.hdc1000_Present)
    print
    print "----------------------"
    print "Future SmartPlantPi Expansions"
    print "----------------------"
    print returnStatusLine("SunAirPlus",config.SunAirPlus_Present)
    print returnStatusLine("Lightning Mode",config.Lightning_Mode)
    print returnStatusLine("Solar Power Mode",config.SolarPower_Mode)

    print returnStatusLine("MySQL Logging Mode",config.enable_MySQL_Logging)
    print
    print "----------------------"
    value = readMoistureValue()
    if (value <= state.Alarm_Moisture_Sensor_Fault):
    	 print "Moisture Sensor Fault:   Not In Plant or not Present. Value %0.2f%%" % value 
    else:
    	print returnStatusLine("Moisture Sensor",True)
    print "----------------------"
    scheduler = BackgroundScheduler()

    ##############
    # state persistance
    # if pickle file present, read it in
    ##############

    if (os.path.exists('SPPState.pkl')):

    	input = open('SPPState.pkl', 'rb')

    	# Pickle dictionary using protocol 0.
    	state.Moisture_Threshold = pickle.load(input)
    	state.EnglishMetric = pickle.load(input)
    	state.Alarm_Temperature = pickle.load(input)
    	state.Alarm_Moisture = pickle.load(input)
    	state.Alarm_Water = pickle.load(input)
    	state.Alarm_Air_Quality = pickle.load(input)
    	state.Alarm_Active = pickle.load(input)

    	input.close()
	



    scheduler.add_listener(ap_my_listener, apscheduler.events.EVENT_JOB_ERROR)	


    # prints out the date and time to console
    scheduler.add_job(tick, 'interval', seconds=60)

    # blink optional life light
    scheduler.add_job(blinkLED, 'interval', seconds=5, args=[1,0.250])


    # update device state
    scheduler.add_job(updateState, 'interval', seconds=10)

    # check for alarms
    scheduler.add_job(checkForAlarms, 'interval', seconds=15)
    #scheduler.add_job(checkForAlarms, 'interval', seconds=300)


    # send State to PubNub 
    scheduler.add_job(publishStateToPubNub, 'interval', seconds=10)

    # check and water  
    scheduler.add_job(checkAndWater, 'interval', minutes=15)

	
    # save state to pickle file 
    scheduler.add_job(saveState, 'interval', minutes=30)

	
	
    # start scheduler
    scheduler.start()
    print "-----------------"
    print "Scheduled Jobs" 
    print "-----------------"
    scheduler.print_jobs()
    print "-----------------"
    
    state.Last_Event = "Started at: "+time.strftime("%Y-%m-%d %H:%M:%S")
    publishEventToPubNub()

    if (config.OLED_Present):
        if (DEBUG):
             print "Attempt OLEDLock acquired"
        OLEDLock.acquire()
        if (DEBUG):
             print "OLEDLock acquired"
	# display logo
    	image = Image.open('SmartPlantPiSquare128x64.ppm').convert('1')

	display.image(image)
	display.display()
	time.sleep(3.0)
	display.clear()

	Scroll_SSD1306.addLineOLED(display,  ("    Welcome to "))
        Scroll_SSD1306.addLineOLED(display,  ("  SmartPlant Pi "))
        if (DEBUG):
             print "Attempt OLEDLock released"
        OLEDLock.release()
        if (DEBUG):
             print "OLEDLock released"

    # set up interrupts to handle flowsensor
    GPIO.add_event_detect(config.FlowSensorPin,GPIO.FALLING,callback=flowSensorEventHandler, bouncetime=100)
    
    # set up interrupts to handle buttonClick
    GPIO.add_event_detect(config.buttonClick,GPIO.FALLING,callback=buttonClickEventHandler, bouncetime=100)
    
     
    
    # initialize variables
    #
    state.Pump_Water_Full = False
    
    try: 
            
       
            updateState()

            checkAndWater()

	    #############
	    #  Main Loop
    	    #############
            
	    jobRotaryTimeOut = None

            while True:
		# other no scheduled periodic events go in here
		time.sleep(0.5)
		if (DEBUG):
			print "SPP_State=%s ROTARY_State=%s" % ( state.SPP_Values[state.SPP_State],state.ROTARY_Values[state.ROTARY_State])
		
		# Check and Intepret Stand Alone Button
	        if (buttonPush == True):
                        # deal with the button Push
                        if (DEBUG):
                                print "button State = ", buttonState
                        buttonPush = False
			# check for Alarm state
                        if (DEBUG):
				print " button == True SPP_State=%s ROTARY_State=%s" % ( state.SPP_Values[state.SPP_State],state.ROTARY_Values[state.ROTARY_State])
			if (state.SPP_State == state.SPP_States.Alarm):
				interpretButton.deactivateAlarms()
			else:
				interpretButton.interpretButton(display, OLEDLock, buttonState)
			saveState()

		# Check and Interpret Rotary Dial and Button 
		jobRotaryTimeOut = interpretRotary.interpretRotary(rotary, display, OLEDLock, scheduler,publishStatusToPubNub, jobRotaryTimeOut, updateState, publishAlarmToPubNub, saveState)



    except KeyboardInterrupt:  
    	    # here you put any code you want to run before the program   
    	    # exits when you press CTRL+C  
            print "exiting program" 
    #except:  
    	    # this catches ALL other exceptions including errors.  
    	    # You won't get any error messages for debugging  
    	    # so only use it once your code is working  
            #    	print "Other error or exception occurred!"  
  
    finally:  
	    #time.sleep(5)
    	    #GPIO.cleanup() # this ensures a clean exit 
	    stopPump()
	    saveState()

	    print "done"
