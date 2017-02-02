#
#
# SDL_Pi_RotaryButton
# Raspberry Pi Driver for the SwitchDoc Labs RotaryButton Breakout Board
#
# SwitchDoc Labs
# January 2017
#
# Version 1.1



import sys
import os
import RPi.GPIO as GPIO
import time
import threading

# default constants

SDL_Pi_RotaryButton_Enc_A = 4
SDL_Pi_RotaryButton_Enc_B = 5
SDL_Pi_RotaryButton_RotaryButtonClick = 21



class SDL_Pi_RotaryButton:
        def __init__(self, ENC_A=SDL_Pi_RotaryButton_Enc_A, ENC_B=SDL_Pi_RotaryButton_Enc_B, RotaryButtonClick=SDL_Pi_RotaryButton_RotaryButtonClick  ):
                

		GPIO.setmode(GPIO.BCM)
		self._rotaryButtonPush = False
		self._rotaryButtonPushCount = 0
		# button sensor setup
		GPIO.setup(SDL_Pi_RotaryButton_RotaryButtonClick, GPIO.IN )

		self._done = False	
	
		# encoder setup
	
		GPIO.setup(SDL_Pi_RotaryButton_Enc_A, GPIO.IN)
		GPIO.setup(SDL_Pi_RotaryButton_Enc_B, GPIO.IN)
	
		# interrupt service routine vars
		self._Rotary_Counter = 0
		self._Current_A = 1
		self._Current_B = 1
		self._LockRotary = threading.Lock()      # create lock for rotary switch

		self._intermediateValue = 0.0
                
             	#set up interrupts to handle encoder Pin 1 ()
    		GPIO.add_event_detect(SDL_Pi_RotaryButton_Enc_A,GPIO.RISING,callback=self.Enc_EventHandler)
    		# set up interrupts to handle encoder Pin 1 ()
    		GPIO.add_event_detect(SDL_Pi_RotaryButton_Enc_B,GPIO.RISING,callback=self.Enc_EventHandler)  

		#set up interrupt for button
		GPIO.add_event_detect( SDL_Pi_RotaryButton_RotaryButtonClick, GPIO.FALLING,callback=self.rotaryButtonClickEventHandler, bouncetime=300)

	# handle the encoder Pin1 event
	def Enc_EventHandler (self,A_or_B):


                                       # read both of the switches
   		self._Switch_A = GPIO.input(SDL_Pi_RotaryButton_Enc_A)
   		self._Switch_B = GPIO.input(SDL_Pi_RotaryButton_Enc_B)
                # now check if state of A or B has changed
                # if not that means that bouncing caused it
   		if self._Current_A == self._Switch_A and self._Current_B == self._Switch_B:      # Same interrupt as before (Bouncing)?
             		return                              		 # ignore interrupt!

   		self._Current_A = self._Switch_A                        # remember new state
   		self._Current_B = self._Switch_B                        # for next bouncing check


   		if (self._Switch_A and self._Switch_B):                  # Both one active? Yes -> end of sequence
      			self._LockRotary.acquire()                 # get lock
      			if A_or_B == SDL_Pi_RotaryButton_Enc_B:           # Turning direction depends on
                   		self._Rotary_Counter -= 1          # which input gave last interrupt
      			else:                                # so depending on direction either
                   		self._Rotary_Counter += 1          # increase or decrease counter
      			self._LockRotary.release()                 # and release lock
   		return                                       # return 

	def readRotary(self,currentValue, bottomRange, topRange, increment, timeout, buttonTimesOut):
        	
        	# read value
		self._currentValue = currentValue

	        # because of threading make sure no thread
            	# changes value until we get them
           	# and reset them

            	self._LockRotary.acquire()               # get lock for rotary switch
            	NewCounter = self._Rotary_Counter         # get counter value
            	self._Rotary_Counter = 0                  # RESET IT TO 0
        	self._done = False
            	self._LockRotary.release()               # and release lock

		# start the worker thread to read
		t = threading.Thread(target=self._readRotaryThread, args=(bottomRange, topRange, increment, timeout, buttonTimesOut))
    		t.start()



	def _readRotaryThread(self,bottomRange, topRange, increment, timeout, buttonTimesOut):
        	startTime = time.time()
        	self._done = False
        	while (not self._done):
            		time.sleep(0.1)
			self._LockRotary.acquire() 
			NewCounter = self._Rotary_Counter
			self._Rotary_Counter = 0
            		self._LockRotary.release() 
            		if (NewCounter !=0):               # Counter has CHANGED
                		startTime = time.time()   # reset timeout
                		self._currentValue = self._currentValue + NewCounter*abs(NewCounter)*increment   # Decrease or increase value

                		if (self._currentValue > topRange):
                    			self._currentValue = topRange
                		if (self._currentValue < bottomRange):
                    			self._currentValue = bottomRange


            		if (self._rotaryButtonPush == True) and (buttonTimesOut == True):
                		self._rotaryButtonPush = False
                		self._done = True
            		# check for timeout
            		if (time.time() > startTime + timeout):
                		self._done = True


                self._done = True
        	return 

	
	def checkIfRotaryDone(self):
		return self._done	

	def readCurrentValue(self):
		return self._currentValue	

	# handle the button click event
	def rotaryButtonClickEventHandler (self,pin):
    		self._rotaryButtonPush = True
		self._rotaryButtonPushCount = self._rotaryButtonPushCount + 1
	
	def hasButtonBeenPushed(self):
		return self._rotaryButtonPush

	def clearButtonBeenPushed(self):
		self._rotaryButtonPush = False
		self._rotaryButtonPushCount = 0

	def buttonPushesSinceLastClear(self):
		return self._rotaryButtonPushCount

