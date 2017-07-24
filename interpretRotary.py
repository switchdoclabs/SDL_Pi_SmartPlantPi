#
# Interpret Rotary and  Button
#
#


import sys
import time



# Check for user imports
try:
            import conflocal as config
except ImportError:
            import config


DEBUGROT= False

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

def returnTemperatureFC(temperature):
	if (state.EnglishMetric == True):
		# return Metric 
		return temperature
	else:
		return (temperature - 32.0)/(9.0/5.0) 

def returnTemperatureCFUnit():
	if (state.EnglishMetric == True):
		# return Metric 
		return "C"
	else:
		return  "F"

from datetime import datetime
from datetime import timedelta

sys.path.append('./SDL_Pi_SSD1306')
sys.path.append('./Adafruit_Python_SSD1306')

import state
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import Adafruit_SSD1306

import Scroll_SSD1306

################
# display
################

def centerText(text,sizeofline):
	textlength = len(text)
	spacesCount = (sizeofline - textlength)/2
	mytext = ""
	if (spacesCount > 0):
		for x in range (0, spacesCount):
			mytext = mytext + " "
	return mytext+text
	
def makeRotaryStatementDisplay(list):
	draw = list[1]	
	font = list[2]
	display = list[3]
	lengthofline = 35

	if (state.ROTARY_State == state.ROTARY_States.MoistureThreshold):
		if (DEBUGROT):
			print "1-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
		text1 = centerText("Plant Moisture", lengthofline)
		text2 = centerText("Threshold", lengthofline)

	elif (state.ROTARY_State == state.ROTARY_States.AlarmsActive):
		if (DEBUGROT):
			print "1-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
		text1 = centerText("Activate", lengthofline)
		text2 = centerText("Alarms", lengthofline)
					
	elif (state.ROTARY_State == state.ROTARY_States.MoistureAlarm):
		if (DEBUGROT):
			print "1-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
		text1 = centerText("Plant Moisture", lengthofline)
		text2 = centerText("Alarm Level", lengthofline)

	elif (state.ROTARY_State == state.ROTARY_States.AirQualityAlarm):
		if (DEBUGROT):
			print "1-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
		text1 = centerText("Air Quality", lengthofline)
		text2 = centerText("Alarm Level", lengthofline)
	
	elif (state.ROTARY_State == state.ROTARY_States.WaterAlarm):
		if (DEBUGROT):
			print "1-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
		text1 = centerText("Activate", lengthofline)
		text2 = centerText("Water Alarm", lengthofline)

	elif (state.ROTARY_State == state.ROTARY_States.TemperatureAlarm):
		if (DEBUGROT):
			print "1-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
		text1 = centerText("Temperature", lengthofline)
		text2 = centerText("Alarm Level", lengthofline)

	elif (state.ROTARY_State == state.ROTARY_States.EnglishMetric):
		if (DEBUGROT):
			print "1-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
		text1 = centerText("Select English", lengthofline)
		text2 = centerText("Or Metric", lengthofline)
					



	draw.text((0, 0),    text1,  font=font, fill=255)
	draw.text((0, 1*12),    text2,  font=font, fill=255)


	image = list[0]
	display.image(image)	
	display.display()

def startRotaryStatementDisplay(display):

	width = 128
	height = 64
	top = 0
	lineheight = 10
	currentLine = 0
	offset = 0
	
	image = Image.new('1', (width, height))
	draw = ImageDraw.Draw(image)
	# Load default font.
	#font = ImageFont.load_default()
	font = ImageFont.truetype('/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf', 12)
	#font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMono.ttf', 12)
	display.clear()
	display.display()
	return [image, draw, font, display]

def finishRotaryStatementDisplay(list):
	image = list[0]
	display = list[3]
	display.clear()
	display.display()

def setupLabelRotaryOLEDDisplay(display):
	
	# acquire OLED DIsplay and set up Rotary Lables acccording to state
        if (config.OLED_Present):
		
		list = startRotaryStatementDisplay(display)
		makeRotaryStatementDisplay(list)
		return list

def displayRotaryValueOLEDDisplay(list, text,lengthofline=18):

	image = list[0]
	draw = list[1]
	font = list[2]
	display = list[3]
	font = ImageFont.truetype('/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf', 25)
	draw.rectangle((0,3*12-2,128,6*12+2), outline=0, fill=255)
	draw.text((0, 3*12-4),    centerText(text, lengthofline),  font=font, fill=0)


	display.image(image)	
	display.display()

	return [image, draw, font, display]
	
	
def closeRotaryOLEDDisplay(list):

	finishRotaryStatementDisplay(list)


###########
# Rotary
###########


def timeoutOnRotarySelect():
	state.SPP_State =state.SPP_States.Rotary
	if (DEBUGROT):
		print "rotaryButtonSelectEnd timeout"


def interpretRotary(rotary, display, OLEDLock, scheduler, publishStatusToPubNub, jobRotaryTimeOut, updateState, publishAlarmToPubNub, saveState ):

		# Now check for Rotary Input
		if (rotary.hasButtonBeenPushed()):
			if (DEBUGROT):
				print "Rotary Button Pushed"
			doTimeOut = False
			if (DEBUGROT):
				print "0-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
			if (state.SPP_State != state.SPP_States.RotarySelect):
				rotaryStartTime = time.time()
				doTimeOut = True

			if (state.SPP_State == state.SPP_States.RotarySelect):
				# we are already in select mode, so we must cancel timeout
				scheduler.remove_job(jobRotaryTimeOut.id)
				# tell to start timeout again
				rotaryStartTime = time.time()
				doTimeOut = True
				
			state.SPP_State = state.SPP_States.RotarySelect
            		publishStatusToPubNub()
			Push_Count = rotary.buttonPushesSinceLastClear()
			rotary.clearButtonBeenPushed()
	
			# key is state advances per button push 	
	 		# Select what to change
			if (DEBUGROT):
				print "pre state", state.ROTARY_State
			state.ROTARY_State = ((state.ROTARY_State + Push_Count) % 8) # mod 8 to loop around	

			if (state.ROTARY_State == 0):
				state.ROTARY_State = 1   # Skip going to idle state
			if (DEBUGROT):
				print "post state", state.ROTARY_State

			# 0 push - idle
			# 1 push -  Moisture Threshold
			# 2 push -  Activate Alarms 
			# 3 push -  Moisture Alarm
			# 4 push - Air Quality Sensor Alarm
			# 5 push - Water Alarm
			# 6 push - Temperature Alarm
			# 7 push - English or Metric Units

			if (DEBUGROT):
				print "rotary_state = ", state.ROTARY_Values[state.ROTARY_State]	
		
	
			if (DEBUGROT):
				print "In state.SPP_States.RotarySelect"

			if (doTimeOut == True):
				# setup 3 second timeout on Rotary Select
				rotaryEndTime = datetime.now() + timedelta(seconds=3)
				try:
					scheduler.remove_job(jobRotaryTimeOut.id)
					if (DEBUGROT):
						print "job removed:", jobRotaryTimeOut.id
				except:
					if (jobRotaryTimeOut is not None): 
						if (DEBUGROT):
							print "previous job does not exist:", jobRotaryTimeOut.id
					else:
						if (DEBUGROT):
							print "No previous job "
	
				jobRotaryTimeOut = scheduler.add_job(timeoutOnRotarySelect, 'date', run_date=rotaryEndTime)
				if (DEBUGROT):
					print "Select Job Scheuduled: ", jobRotaryTimeOut.id
					print "Select rotaryStartTime:", str(time.strftime("%H:%M:%S", time.localtime(rotaryStartTime)))
					print "Select Job Scheuduled at: ", jobRotaryTimeOut.next_run_time


	
		# Now deal with Rotary
		if (state.SPP_State == state.SPP_States.Rotary):
			if (DEBUGROT):
				print "In state.SPP_States.Rotary"
	    		#readRotary(currentValue, bottomRange, topRange, increment, timeout, buttonTimesOut)
			
			# 0 push - idle
			# 1 push -  Moisture Threshold
			# 2 push -  Activate Alarms 
			# 3 push -  Moisture Alarm
			# 4 push - Air Quality Sensor Alarm
			# 5 push - Water Alarm
			# 6 push - Temperature Alarm
			# 7 push - English or Metric Units


			# set up appropriate values
			if (DEBUGROT):
                               print  "Attempt OLEDLock acquired"
                        OLEDLock.acquire()
			if (DEBUGROT):
                               print  "OLEDLock acquired"

			list = setupLabelRotaryOLEDDisplay(display)

			if (state.ROTARY_State == state.ROTARY_States.MoistureThreshold):
				if (DEBUGROT):
					print "2-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
				currentValue = state.Moisture_Threshold
		 		bottomRange =5.0 
				topRange = 100.0
				increment = 1
				timeout = 10.0
				buttonTimesOut = True

			elif (state.ROTARY_State == state.ROTARY_States.AlarmsActive):
				if (DEBUGROT):
					print "2-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 

				if (state.Alarm_Active == True):
					currentValue = 1
				else:
					currentValue = 0
		 		bottomRange =0 
				topRange = 1
				increment = 1
				timeout = 10.0
				buttonTimesOut = True

			elif (state.ROTARY_State == state.ROTARY_States.MoistureAlarm):
				if (DEBUGROT):
					print "2-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
				currentValue = state.Alarm_Moisture
		 		bottomRange =5.0 
				topRange = 100.0
				increment = 1
				timeout = 10.0
				buttonTimesOut = True

			elif (state.ROTARY_State == state.ROTARY_States.AirQualityAlarm):
				if (DEBUGROT):
					print "2-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
				currentValue = state.Alarm_Air_Quality
		 		bottomRange =100 
				topRange = 16000.0
				increment = 100
				timeout = 10.0
				buttonTimesOut = True

			elif (state.ROTARY_State == state.ROTARY_States.WaterAlarm):
				if (DEBUGROT):
					print "2-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
				if (state.Alarm_Water == True):
					currentValue = 1
				else:
					currentValue = 0
		 		bottomRange =0 
				topRange = 1
				increment = 1
				timeout = 10.0
				buttonTimesOut = True


			elif (state.ROTARY_State == state.ROTARY_States.TemperatureAlarm):
				if (DEBUGROT):
					print "2-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
				currentValue = returnTemperatureCF(state.Alarm_Temperature )
		 		bottomRange =-20.0 
				topRange = 100.0
				increment = 1
				timeout = 10.0
				buttonTimesOut = True


			elif (state.ROTARY_State == state.ROTARY_States.EnglishMetric):
				if (DEBUGROT):
					print "2-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
				if (state.EnglishMetric == True):
					currentValue = 1
				else:
					currentValue = 0
		 		bottomRange =0 
				topRange = 1
				increment = 1
				timeout = 10.0
				buttonTimesOut = True

	    		rotary.readRotary(currentValue, bottomRange, topRange, increment, timeout, buttonTimesOut)
	    		while (not rotary.checkIfRotaryDone()):

				currentValue = rotary.readCurrentValue()
				if (DEBUGROT):
            				print "rotary current value = ",currentValue
				# handle Text Responses
				if (state.ROTARY_State == state.ROTARY_States.AlarmsActive):
					if (currentValue == 1):
						displayRotaryValueOLEDDisplay(list, "Active",14 )
					else:
						displayRotaryValueOLEDDisplay(list, "Disabled", 14  )

				elif (state.ROTARY_State == state.ROTARY_States.EnglishMetric):
					if (currentValue == 1):
						displayRotaryValueOLEDDisplay(list, "Metric", 14 )
					else:
						displayRotaryValueOLEDDisplay(list, "English" , 14)

				elif (state.ROTARY_State == state.ROTARY_States.WaterAlarm):
					if (currentValue == 1):
						displayRotaryValueOLEDDisplay(list, "Active",14 )
					else:
						displayRotaryValueOLEDDisplay(list, "Disabled", 14  )

				else:
					displayRotaryValueOLEDDisplay(list, "%i.0" % currentValue)
					
				
            			time.sleep(0.2)
		
			if (DEBUGROT):
	    			print "final rotary value =", currentValue
			# Consume the finishing click 
			rotary.clearButtonBeenPushed()
			try:
				scheduler.remove_job(jobRotaryTimeOut.id)
				if (DEBUGROT):
					print "job removed:", jobRotaryTimeOut.id
			except:
				if (jobRotaryTimeOut is not None): 
					if (DEBUGROT):
						print "previous job does not exist:", jobRotaryTimeOut.id
				else:
					print "No previous job "
			
	
			# interpret appropriate values

			if (state.ROTARY_State == state.ROTARY_States.MoistureThreshold):
				if (DEBUGROT):
					print "3-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
				state.Moisture_Threshold = currentValue

			elif (state.ROTARY_State == state.ROTARY_States.AlarmsActive):
				if (DEBUGROT):
					print "3-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
				if (currentValue == 1):
					state.Alarm_Active = True
					publishAlarmToPubNub("None")
				else:
					state.Alarm_Active = False
					publishAlarmToPubNub("")
					
			elif (state.ROTARY_State == state.ROTARY_States.MoistureAlarm):
				if (DEBUGROT):
					print "3-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
				state.Alarm_Moisture = currentValue

			elif (state.ROTARY_State == state.ROTARY_States.AirQualityAlarm):
				if (DEBUGROT):
					print "3-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
				state.Alarm_Air_Quality = currentValue

			elif (state.ROTARY_State == state.ROTARY_States.WaterAlarm):
				if (DEBUGROT):
					print "3-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
				state.Alarm_Water = currentValue

			elif (state.ROTARY_State == state.ROTARY_States.TemperatureAlarm):
				if (DEBUGROT):
					print "3-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
				state.Alarm_Temperature = returnTemperatureFC(currentValue)

			elif (state.ROTARY_State == state.ROTARY_States.EnglishMetric):
				if (DEBUGROT):
					print "3-in ROTARY_State", state.ROTARY_Values[state.ROTARY_State] 
				if (currentValue == 1):
					state.EnglishMetric = True
				else:
					state.EnglishMetric = False
					


			closeRotaryOLEDDisplay(list)
			saveState()

			if (DEBUGROT):
                               print  "Attempt OLEDLock released"
			OLEDLock.release()
			if (DEBUGROT):
                               print  "OLEDLock released"
			state.ROTARY_State = state.ROTARY_States.Idle
			state.SPP_State = state.SPP_States.Monitor
            		publishStatusToPubNub()
			scheduler.add_job(updateState )


		return jobRotaryTimeOut
	
	
