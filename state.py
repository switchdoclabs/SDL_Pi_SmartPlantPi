# 
# contains all the state variables for SmartPlantPi
#

##################
#  English or Metric
##################
# if False, then English
# if True, then Metric
EnglishMetric = False 

##################
# Sunlight sensor variable
##################

Sunlight_Vis = 0
Sunlight_IR = 0
Sunlight_UV = 0.0
Sunlight_UVIndex = 0.0


##################
# Mositure Sensor
##################
Moisture_Humidity = 100.0

#water below this limit

Moisture_Threshold = 65.0   
##################
# Pump State
##################

Pump_Running = False
Pump_Flow_Rate = 0
Pump_Last_Flow_Volume = 0
Pump_Current_Flow_Volume = 0

Pump_Water_Full = False
##################
# Temp/Humid sensor
##################

Temperature = 0.0
Humidity = 0.0

##################
# Air Quality Sensor
##################

AirQuality_Sensor_Value = 0
AirQuality_Sensor_Number = 4
AirQuality_Sensor_Text = ""


##################
# Alarm States
##################
Alarm_Temperature = 5.0  
Alarm_Moisture = 60.0
Alarm_Water = False
Alarm_Air_Quality = 10000 
Alarm_Moisture_Sensor_Fault = 10.0

Alarm_Active = False
Alarm_Cancel = False

##################
# Internal States
##################

# State Enum
class SPP_States():
    Idle = 0
    Monitor = 1
    Watering = 2
    RotarySelect = 3
    Rotary = 4
    Alarm = 5
    Sampling = 6
    Button = 7

SPP_Values = ["Idle", "Monitor", "Watering", "Rotary Select", "Rotary", "Alarm", "Sampling", "Button"]

SPP_State = SPP_States.Monitor

Last_Event = ""


# rotary states
class ROTARY_States():
	Idle = 0
	MoistureThreshold = 1
	AlarmsActive = 2
	MoistureAlarm = 3
	AirQualityAlarm = 4
	WaterAlarm = 5
	TemperatureAlarm = 6
	EnglishMetric = 7
	
ROTARY_Values = ["Idle","Moisture Threshold", "Activate Alarms", "Moisture Alarm", "Air Quality Alarm", "Water Alarm", "Temperature Alarm", "English or Metric"]

ROTARY_State = ROTARY_States.Idle



