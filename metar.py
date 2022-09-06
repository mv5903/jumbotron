#metar.py - Modified from JJSilva's NeoSectional Script located; https://github.com/JJSilva/NeoSectional/blob/master/metar.py
#This version adds a few more features, including flashing airports whose wind speed is greater than the set value. Typically 15 kts
#It also will simulate lightning at airports who are reporting Thunderstorms, Tornados, etc.
#This version also encorporates dimming using a module such as IC238 Light Sensor. The script works fine, without the sensor.
#Here is a link to Amazon for an example of the light sensors; https://www.amazon.com/gp/product/B07PFSHX71/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1
#Modify the ./NeoSectional/airports file with the airport codes to display on the map. Use "NULL" to skip a bulb.
#One note, the last airport listed in the "airport" file cannot be "NULL" otherwise the script will light all the LED's White.
import urllib2
import xml.etree.ElementTree as ET
import time
from neopixel import *
import sys
import os

#setup for IC238 Light Sensor for LED Dimming, does not need to be commented out if sensor is not used
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.IN)

# LED strip configuration:
LED_COUNT      = 26      #Number of LED pixels. Change this value to match the number of LED's being used on map
LED_PIN        = 18      #GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10     #GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  #LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       #DMA channel to use for generating signal (try 5)
LED_INVERT     = False   #True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       #set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   #Strip type and colour ordering
LED_BRIGHTNESS = 255	 #starting brightness. It may be changed using user settings below.

#User defined items to be set
max_wind_speed = 15      #Any speed above will flash the LED for the appropriate airport
toggle = 0		#initialize blink toggle. 0 will start the lights in the ON position. 1 will start with lights OFF.
blink_pause = .8	#Determines how quickly the LED's blink if winds are more than max_wind_speed in seconds
lghtnon = .08		#Lightning on interval in seconds
lghtnoff = .12		#Lightning off interval in seconds
update_interval = 15	#Number of MINUTES between FAA updates - 15 minutes is a good compromise

			#Set LED Colors. Change numbers in paranthesis. The order is (Green,Red,Blue). Each has a range of 0-255.
color_vfr = Color(255,0,0)	#Full bright Green
color_mvfr = Color(0,0,255)	#Full bright Blue
color_ifr = Color(0,255,0)	#Full bright Red
color_lifr = Color(0,255,255)	#Full bright Magenta
color_nowx = Color(200,200,200) #Slightly dimmed white
color_black = Color(0,0,0)	#Black/Off
color_yellow = Color(255,255,0) #Full bright Yellow (used for legend on lightning/thunderstorms)

legend = 1              #1 = Yes, 0 = No. Use defined pins to set up a legend using LEDs. Pay notice to legend_hiwinds and legend_lghtn in relation to Legend.
legend_hiwinds = 1	#1 = Yes, 0 = No. the legend can display just the flight categories, or high winds as well
legend_lghtn = 1	#1 = Yes, 0 = No. the legend can display just the flight categories, or Lightning/Thunderstorm as well
legend_pin_vfr = 19	#Set LED pin number for VFR Legend LED
legend_pin_mvfr = 20	#Set LED pin number for MVFR Legend LED
legend_pin_ifr = 21	#Set LED pin number for IFR Legend LED
legend_pin_lifr = 22	#Set LED pin number for LIFR Legend LED
legend_pin_nowx = 23	#Set LED pin number for No Weather Legend LED
legend_hiwinds_pin = 24 #Set LED pin number for High Winds Legend LED
legend_lghtn_pin = 25   #Set LED pin number for Thunderstorms Legend LED

hiwindblink = 1		#1 = Yes, 0 = No. Blink the LED for high wind Airports.
lghtnflash = 1		#1 = Yes, 0 = No. Flash the LED for an airport reporting severe weather like TSRA.

dimmed_value = 25	#Range is 0 - 255. This sets the value of LED brightness when sensor detects low ambient light
bright_value = 255	#Range is 0 - 255. This sets the value of LED brightness when sensor detects high ambient light

			#list of METAR weather categories to designate severe weather in area.
			#See https://www.aviationweather.gov/metar/symbol for descriptions. Add or subtract as necessary.
wx_lghtn_ck = ["TS", "TSRA", "TSGR", "+TSRA", "VCSS", "FC", "SQ", "VCTS", "VCTSRA", "VCTSDZ", "LTG"]
iterations = 6		#Number of times that the rainbow animation will run before updating LED colors

#create an instance of NeoPixel
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
strip.begin()

#Rainbow Animation functions - taken from https://github.com/JJSilva/NeoSectional/blob/master/metar.py
def wheel(pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
                return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
                pos -= 85
                return Color(255 - pos * 3, 0, pos * 3)
        else:
                pos -= 170
                return Color(0, pos * 3, 255 - pos * 3)

def rainbowCycle(strip, iterations, wait_ms=2):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256*iterations):
                for i in range(strip.numPixels()):
                        strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
                strip.show()
                #time.sleep(wait_ms/1000.0)

#Start of infintite loop that first updates data from FAA. Then cycles through the LED's to set colors and blinks as necessary
infinite = 1 #Set variable for infinite loop. It doesn't get changed
while (infinite):
	rainbowCycle(strip, iterations)
	print "Updating FAA Weather Data" #Debug

	#read airports file
	with open("/NeoSectional/airports") as f:
    		airports = f.readlines()
	airports = [x.strip() for x in airports]

	#define dictionaries
	mydict = {
		"":""
	}
	mydictwinds = {
		"":""
	}
	mydicttsra = {
		"":""
	}

	#define URL to get weather METARS. This will pull only the latest METAR from the last 2.5 hours. If no METAR reported withing the last 2.5 hours, Airport LED will be white.
	url = "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&mostRecentForEachStation=constraint&hoursBeforeNow=2.5&stationString="

	#build URL to submit to FAA with the proper airports from the airports file
	for airportcode in airports:
        	if airportcode == "NULL":
                	continue
        	url = url + airportcode + ","

	try:
		#print url #Debug
		content = urllib2.urlopen(url).read()
		#Uncomment below to debug retreived FAA data
		#print content
	except:
		pass

	root = ET.fromstring(content)

	#grab the airport category, wind speed and TSRA from the results given from FAA.
	for metar in root.iter('METAR'):
        	if airportcode == "NULL": #if airport code is NULL, then bypass
                	continue
        	stationId = metar.find('station_id').text

		#grab flight category from returned FAA data
        	if metar.find('flight_category') is None: #if category is blank, then bypass
                	print "Skipping"
                	continue
        	flightCateory = metar.find('flight_category').text

		#grab wind speeds from returned FAA data
		if metar.find('wind_speed_kt') is None: #if wind speed is blank, then bypass
			print "Skipping"
			continue
		windspeedkt = metar.find('wind_speed_kt').text

		#grab Thunderstorm info from returned FAA data
        	if metar.find('wx_string') is None: #if weather string is blank, then bypass
                	wxstring = "NONE"
		else:
	        	wxstring = metar.find('wx_string').text

        	print stationId + " " + flightCateory + " " + windspeedkt + " " + wxstring #Debug


		#Check for duplicate airport identifier and skip if found, otherwise store in dictionary
        	if stationId in mydict:
                	print "duplicate, only save first metar category"
        	else:
                	mydict[stationId] = flightCateory #build category dictionary

		if stationId in mydictwinds:
			print "duplicate, only save the first winds"
		else:
			mydictwinds[stationId] = windspeedkt #build windspeed dictionary

        	if stationId in mydicttsra:
                	print "duplicate, only save the first weather"
        	else:
                	mydicttsra[stationId] = wxstring #build thunderstorm dictionary


	#uncomment below to debug dictionarys
	#print mydict
	#print mydictwinds
	#print mydicttsra


	#Uncomment out the following lines to create a Map Legend be sure to also change the numbers to correspond with your LED light positions.
	#Be sure to put a "NULL" at each legend pin position in the ./NeoSectional/airports file so it won't be overwritten.
	#The legend can be disabled in settings. It can be turned on showing only the 5 weather categories, VFR, MVFR, IFR, LIFR, No WX.
	#Or you can add High Winds which will blink, and/or add Lightning/Thunderstorms which will simulate lightning.
	if legend:
		#VFR LED - Green
		strip.setPixelColor(legend_pin_vfr, color_vfr)

		#MVFR - Blue
		strip.setPixelColor(legend_pin_mvfr, color_mvfr)

		#IFR - Red
		strip.setPixelColor(legend_pin_ifr, color_ifr)

		#LIFR - Magenta
		strip.setPixelColor(legend_pin_lifr, color_lifr)

		#No Weather Reported - White
		strip.setPixelColor(legend_pin_nowx, color_nowx) 

		#High Winds - Blinking Blue Light. Can be disabled in the user settings

		#Lightning/Thunderstorms - Flashing Red/Yellow Light. Can be disabled in the user settings

		strip.show()

	#setup timed loop that will run based on the value of update_interval which is a user setting
	timeout_start = time.time()
	while time.time() < timeout_start + (update_interval * 60): #take update interval which is in mins and turn into seconds

		toggle = not(toggle) #used to determine if LED should be on or off

		#Bright light will provide a low input (0). Dark light will provide a high input (1). Full brightness used if no light sensor installed
		if GPIO.input(4) == 1:
    			LED_BRIGHTNESS = dimmed_value
		else:
    			LED_BRIGHTNESS = bright_value
		strip.setBrightness(LED_BRIGHTNESS)

		#start main loop to determine which airports should blink
		i = 0
		for airportcode in airports:
			print ('airport LED number = ' + str(i)) #Debug

			if airportcode == "NULL": #retrieve the color that the LED has been assigned so we can save it for restoring if the LED will be Blinking
				print "NULL" #Debug
				print #Debug
				i = i +1
				continue
			color = color_black

			flightCateory = mydict.get(airportcode,"No")
			print airportcode + " is " + flightCateory #Debug

			if  flightCateory != "No":
				if flightCateory == "VFR":
					#print "VFR" #Debug
					color = color_vfr
				elif flightCateory == "MVFR":
					color = color_mvfr
					#print "MVFR" #Debug
				elif flightCateory == "IFR":
					color = color_ifr
					#print "IFR" #Debug
				elif flightCateory == "LIFR":
					color = color_lifr
					#print "LIFR" #Debug
			else:
				color = color_nowx
				#print "N/A" #Debug

			strip.setPixelColor(i, color)

			#Check the windspeed to determine if the LED should blink
			if hiwindblink: #Check user setting to determine if the map should blink for high winds or not
				windspeedkt = mydictwinds.get(airportcode,"No")
				print airportcode + " winds = " + windspeedkt #Debug

				if windspeedkt != "No":
					if int(windspeedkt) > max_wind_speed:
						if toggle == 0:
							blink = color_black #Turn off LED
							strip.setPixelColor(i, blink)
						else:
							blink = color #Turn on LED
							strip.setPixelColor(i, blink)

				if legend_hiwinds: #Check to see if Legend is being used
					if toggle == 0:
                                                blink = color_black #Turn off LED
                                                strip.setPixelColor(legend_hiwinds_pin, blink)
                                        else:
                                                blink = color_mvfr #Turn on LED Blue
                                                strip.setPixelColor(legend_hiwinds_pin, blink)
				else:
					strip.setPixelColor(legend_hiwinds_pin, color_black)


			#Check to see if wxstring shows a thunderstorm. Flash LED White randomly if so
			if lghtnflash: #Check user setting to determine if the map should lightning flash for severe weather or not
				wxstring = mydicttsra.get(airportcode,"No")
				print " WX = " + wxstring #Debug

				if wxstring <> "NONE" or "NO" or "No":

					if wxstring in wx_lghtn_ck:
						print "YES WEATHER " + wxstring #Debug
						#quickly flash bright yellow to represent lightning
						strip.setPixelColor(i, color_yellow)
						strip.show()
						time.sleep(lghtnon)
						strip.setPixelColor(i, color)
						strip.show()
						time.sleep(lghtnoff)
						strip.setPixelColor(i, color_yellow)
                                		strip.show()
                                		time.sleep(lghtnon)
                                		strip.setPixelColor(i, color)
                                		strip.show()

					else:
						print "NO WEATHER " + wxstring #Debug

				print #Debug

			i = i + 1 #increment to next airport

		#If legend is used and thunderstorms are on 
		if legend_lghtn:
                        #quickly flash bright yellow to represent lightning
                        strip.setPixelColor(legend_lghtn_pin, color_yellow)
                        strip.show()
                        time.sleep(lghtnon)
                        strip.setPixelColor(legend_lghtn_pin, color_ifr)
                        strip.show()
                        time.sleep(lghtnoff)
                        strip.setPixelColor(legend_lghtn_pin, color_yellow)
                        strip.show()
                        time.sleep(lghtnon)
                        strip.setPixelColor(legend_lghtn_pin, color_ifr)
                        strip.show()
		else:
			strip.setPixelColor(legend_lghtn_pin, color_black)

		strip.show()
		time.sleep(blink_pause) #pause Blink before continuing
