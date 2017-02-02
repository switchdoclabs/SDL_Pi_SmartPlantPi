#!/usr/bin/env python
#
# Test SDL_Pi_RotaryButton
#
# January 2017
#

#imports

import sys          
import time
import datetime
import SDL_Pi_RotaryButton



# Main Program

print ""
print "Test SDL_Pi_RotaryButton Version 1.0 - SwitchDoc Labs" 
print ""
print "Sample uses:" 
print "	SDL_Pi_RotaryButton_Enc_A = 4"
print "	SDL_Pi_RotaryButton_Enc_B = 5"
print "	SDL_Pi_RotaryButton_RotaryButtonClick = 21"
print ""            
print "Program Started at:"+ time.strftime("%Y-%m-%d %H:%M:%S")
print ""            


rotary = SDL_Pi_RotaryButton.SDL_Pi_RotaryButton()





print "Reading Rotary"
print "Button stops read Reading Rotary"
# example readRotary
currentValue = 0
# readRotary(currentValue, bottomRange, topRange, increment, timeout, buttonTimesOut)
rotary.readRotary(currentValue, -30, 30, 0.5,10.0, True)
while (not rotary.checkIfRotaryDone()):

	print "rotary current value = ",rotary.readCurrentValue()
	time.sleep(0.2)

print "final rotary value =", rotary.readCurrentValue()

# now show how to use button seperately

print "hit rotary button to quit"
while (not rotary.hasButtonBeenPushed()):
	print "no button"
	time.sleep(0.5)
print "button pushed"

