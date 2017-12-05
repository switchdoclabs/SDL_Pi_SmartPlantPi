#
# Smart Plant Pi Raspberry Pi Software
# SDL_Pi_SmartPlantPi
#
# SwitchDoc Labs July 2017
#

# all SmartPlantPi Documentation on www.switchdoc.com/SmartPlantPi

December 5, 2017:  Release Version 017<BR>
Fixed directory names in testAll.py - thanks Faltek!

November 22, 2017:  Release Version 017<BR>
Read README.md for version class reinstall of Adafruit_Python_GPIO

November 17, 2017:  Release Version 017<BR>
Fixed input name clash from OS Update

July 24, 2017:  Release Version 016<BR>
Fixed DEBUG related issues in interpretRotary and interpretButton

July 20, 2017:  Release Version 015<BR>
Frozen Update State Moisture Detection (Water) Lock up fixed

July 20, 2017:  Release Version 014<BR>
UV Index Typo and JSON update for freeboard.io

June 26, 2017:  Release Version 013<BR>
Accuracy Problem with the HDC1080 Temperature and Humidity Fixed


May 27, 2017:  Fixed Typo in README.md - Thanks Daniels!

April 17, 2017:  Release Version 012<BR>
Modified code (backwardly compatible) to install Grove PowerSave to make Moisture Sensor more reliable and longer lasting<BR>

March 26, 2017:  Release Version 011<BR>
Added Lightning_Mode configuration variable to allow execution <BR>

March 21, 2017:  Release Version 010<BR>
Added SunAirPlus configuration variable to allow execution <BR>

March 17, 2017:  Release Version 009<BR>
Added Alexa configuration variable to block out writing json file<BR>

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

#Installing apscheduler and pil

sudo apt-get install python-pip<BR>

sudo apt-get install python-pil <BR>

sudo pip install --upgrade setuptools pip <BR>

sudo pip install setuptools --upgrade  <BR>
sudo pip install apscheduler <BR>

#Installing PubNub

sudo pip install 'pubnub>=4.0.5' <BR>

Note:  state.py contains constants for running SmartPlantPi (Alarms, etc.) that you may want to change <BR>

config.py contains constants for hook up and other things you may want to change.<BR>
