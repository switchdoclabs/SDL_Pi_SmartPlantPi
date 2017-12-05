#!/usr/bin/env python
#
#
# Test All for Pi Smart Plant 
#
# SwitchDoc Labs, November 2016
#

#imports 

import sys
import RPi.GPIO as GPIO
import time
import threading

#appends
sys.path.append('./SDL_Pi_SSD1306')
sys.path.append('./Adafruit_Python_SSD1306')
sys.path.append('./SDL_Pi_HDC1000')
sys.path.append('./SDL_Pi_SSD1306')
sys.path.append('./Adafruit_Python_SSD1306')
sys.path.append('./SDL_Pi_SI1145')
sys.path.append('./SDL_Pi_RotaryButton')

sys.path.append('./SDL_Pi_Grove4Ch16BitADC/SDL_Adafruit_ADS1x15')

import SDL_Pi_HDC1000
import SDL_Pi_RotaryButton

import Adafruit_SSD1306

import Scroll_SSD1306

import SDL_Pi_SI1145

from SDL_Adafruit_ADS1x15 import ADS1x15

import AirQualitySensorLibrary 

# Check for user imports
try:
            import conflocal as config
except ImportError:
            import config

            if (config.enable_MySQL_Logging == True):
                 import MySQLdb as mdb


###############
#initialization
###############

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


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
    global buttonPush
    print "handling button Click event"
    buttonPush = True

###############
# rotary dial and button setup
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

###############
# Sunlight SI1145 Sensor Setup
################


Sunlight_Sensor = SDL_Pi_SI1145.SDL_Pi_SI1145()

try:
        visible = Sunlight_Sensor.readVisible()
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



# Main Program

print ""
print "Test All Pi SmartPlant Devices Version 1.0 - SwitchDoc Labs"
print ""
print "Program Started at:"+ time.strftime("%Y-%m-%d %H:%M:%S")
print ""

if (config.OLED_Present):
      Scroll_SSD1306.addLineOLED(display,  ("    Welcome to "))
      Scroll_SSD1306.addLineOLED(display,  ("  Pi Smart_Plant "))

# set up interrupts to handle flowsensor
GPIO.add_event_detect(config.FlowSensorPin,GPIO.FALLING,callback=flowSensorEventHandler, bouncetime=100)

# set up interrupts to handle buttonClick
GPIO.add_event_detect(config.buttonClick,GPIO.FALLING,callback=buttonClickEventHandler, bouncetime=100)

############
# Setup Moisture Pin for GrovePowerSave
############
GPIO.setup(config.moisturePower,GPIO.OUT)
GPIO.output(config.moisturePower, GPIO.LOW)

#

try:  
	startPump()


	NbTopsFan = 0   #Set NbTops to 0 ready for calculations
  	#sei();      #Enables interrupts
  	time.sleep(1);   #Wait 1 second
  	#cli();      #Disable interrupts
  	Calc = 60*(NbTopsFan * 60 / 73); #Pulse frequency x 60) / 73Q, = flow rate in L/hour 
  	print " L/hour %6.2f" % Calc 

	NbTopsFan = 0   #Set NbTops to 0 ready for calculations
  	#sei();      #Enables interrupts
  	time.sleep(1);   #Wait 1 second
  	#cli();      #Disable interrupts
  	Calc = 60*(NbTopsFan * 60 / 73); #Pulse frequency x 60) / 73Q, = flow rate in L/hour 
  	print " L/hour %6.2f"% Calc 

	NbTopsFan = 0   #Set NbTops to 0 ready for calculations
  	#sei();      #Enables interrupts
  	time.sleep(1);   #Wait 1 second
  	#cli();      #Disable interrupts
  	Calc = 60*(NbTopsFan * 60 / 73); #Pulse frequency x 60) / 73Q, = flow rate in L/hour 
  	print " L/hour %6.2f"% Calc 

	NbTopsFan = 0   #Set NbTops to 0 ready for calculations
  	#sei();      #Enables interrupts
  	time.sleep(1);   #Wait 1 second
  	#cli();      #Disable interrupts
  	Calc = 60*(NbTopsFan * 60 / 73); #Pulse frequency x 60) / 73Q, = flow rate in L/hour 
  	print " L/hour %6.2f"% Calc 

	NbTopsFan = 0   #Set NbTops to 0 ready for calculations
  	#sei();      #Enables interrupts
  	time.sleep(1);   #Wait 1 second
  	#cli();      #Disable interrupts
  	Calc = 60*(NbTopsFan * 60 / 73); #Pulse frequency x 60) / 73Q, = flow rate in L/hour 
  	print " L/hour %6.2f"% Calc 

	stopPump()

        # read temp humidity

        degrees= hdc1000.readTemperature()
        humidity = hdc1000.readHumidity()

        print 'Temp             = {0:0.3f} deg C'.format(degrees)
        print 'Humidity         = {0:0.2f} %'.format(humidity)

        # OLED display

        if (config.OLED_Present):
                Scroll_SSD1306.addLineOLED(display,  ("Temp = \t%0.2f C")%(degrees))
                Scroll_SSD1306.addLineOLED(display,  ("Humidity =\t%0.2f %%")%(humidity))

        print "----------------- "
        if (config.Sunlight_Present == True):
                            print " Sunlight Vi/IR/UV Sensor"
        else:
                            print " Sunlight Vi/IR/UV Sensor Not Present"
        print "----------------- "

        if (config.Sunlight_Present == True):
                ################
                SunlightVisible = Sunlight_Sensor.readVisible()
                SunlightIR = Sunlight_Sensor.readIR()
                SunlightUV = Sunlight_Sensor.readUV()
                SunlightUVIndex = SunlightUV / 100.0
                print 'Sunlight Visible:  ' + str(SunlightVisible)
                print 'Sunlight IR:       ' + str(SunlightIR)
                print 'Sunlight UV Index: ' + str(SunlightUVIndex)
                ################

        if (config.OLED_Present):
                Scroll_SSD1306.addLineOLED(display,  ("Sunlight = \t%0.2f Lum")%(SunlightVisible))


        if (config.ADS1115_Present):
            GPIO.output(config.moisturePower, GPIO.HIGH)
            Moisture_Humidity   = ads1115.readADCSingleEnded(config.moistureADPin, gain, sps)/7 # AIN0 wired to AirQuality Sensor
            GPIO.output(config.moisturePower, GPIO.LOW)

            print Moisture_Humidity
	    Moisture_Humidity = Moisture_Humidity / 7.0
            if (Moisture_Humidity >100): 
                Moisture_Humidity = 100;
            print "Moisture Humidity = %0.2f" % (Moisture_Humidity)
            print"------------------------------"

            sensor_value =  AirQualitySensorLibrary.readAirQualitySensor(ads1115)

            sensorList = AirQualitySensorLibrary.interpretAirQualitySensor(sensor_value)
            print "Sensor Value=%i --> %s  | %i"% (sensor_value, sensorList[0], sensorList[1])
            
                 
        print "-----------------------"
        print "Reading Rotary"
        print "Rotary Button stops read Reading Rotary"
        print "-----------------------"
        # example readRotary
        currentValue = 0
        # readRotary(currentValue, bottomRange, topRange, increment, timeout, buttonTimesOut)
        rotary.readRotary(currentValue, -30, 30, 0.5,10.0, True)
        while (not rotary.checkIfRotaryDone()):

               print "rotary current value = ",rotary.readCurrentValue()
               time.sleep(0.2)

        print "final rotary value =", rotary.readCurrentValue()

        # now show how to use button seperately

        print "-----------------------"
	print "hit rotary button to quit"
        print "-----------------------"
	i = 0
        while (not rotary.hasButtonBeenPushed()):
               print "push rotary button to quit"
               time.sleep(0.5)
	       i=i+1
	       if (i > 25):
			print "-----------------------"
			print "no button pushed - exiting"
			print "-----------------------"
			break
        if (i < 25):
		print "-----------------------"
		print "button pushed" 
		print "-----------------------"


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
	print "done with testAll"
