#
# Smart Plant Pi Raspberry Pi Software
# SDL_Pi_SmartPlantPi
#
# SwitchDoc Labs February 2017
#

# all SmartPlantPi Documentation on www.switchdoc.com/SmartPlantPi

February 24, 2017:  Release Version 008<BR>
Added code for Moisture Sensor Fault detection and blocking watering in the case of a fault<BR>

February 2, 2017:  Release Version 007<BR>
Removed Debug lines<BR>

February 2, 2017:  Initial Release Version 006

# basic install instructions for supporting libraries

sudo apt-get update <BR>
sudo apt-get dist-upgrade <BR>

sudo apt-get install build-essential python-pip python-dev python-smbus git <BR>
git clone https://github.com/adafruit/Adafruit_Python_GPIO.git <BR>
cd Adafruit_Python_GPIO <BR>
sudo python setup.py install <BR>


Make sure you installed I2C as in this link:

https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c

#Installing apscheduler

sudo pip install --upgrade setuptools pip <BR>

sudo pip install setuptools --upgrade  <BR>
sudo pip install apscheduler <BR>

#Installing PubNub

sudo pip install 'pubnub>=4.0.5' <BR>

Note:  state.py contains constants for running SmartPlantPi (Alarms, etc.) that you may want to change <BR>

config.py contains constants for hook up and other things you may want to change.<BR>
