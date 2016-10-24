from __future__ import print_function
from omxplayer import OMXPlayer
from termcolor import colored
import RPi.GPIO as GPIO
import time, sys

# Pin and varible assignments
trig = 23
echo = 26
triggerDistance = 60		# Trigger distance to trigger video.
nearDistance = 2		# Will display a self-ping error if below this value.
rewind_counter = 0		# Counts number of times through the control flow.

# Raspberry Pi GPIO Setup Stuff
GPIO.setmode (GPIO.BCM)
GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)
GPIO.setwarnings(False)

# Initialize OMXPlayer
player = OMXPlayer('/home/pi/Desktop/dolby_leaf-DWEU.mkv')
player.play()
time.sleep(5)
player.pause()

def get_distance():
	global trig, echo

	if GPIO.input (echo):
		return (1000)

	distance = 0

	GPIO.output (trig,False)
	time.sleep (0.05)

	GPIO.output (trig,True)
	dummy_variable = 0
	dummy_variable = 0
	
	GPIO.output (trig,False)
	time1, time2 = time.time(), time.time()
	
	while not GPIO.input (echo):
		time1 = time.time()
		if time1 - time2 > 0.02:
			distance = 1000
			break
		
	if distance == 1000:
		return (distance)
	
	while GPIO.input (echo):
		time2 = time.time()
		if time2 - time1 > 0.02:
			distance = 1000
			break
		
	if distance == 1000: 
		return (distance)
																		
	distance = (time2 - time1) / 0.00000295 / 2 / 10
  
	distance = round(distance, 2)

	return (distance)

def fadeOut(rateO):
	volO = 1.0
	while volO > 0:
		volO -= 0.01
		volO = round(volO, 2)
		time.sleep(rateO)
#		pygame.mixer.music.set_volume(volO)	# This needs to be changed to the OMXWrapper API
		print(colored('Fading out: ', 'green'), volO, end='\r')
		sys.stdout.flush()
	
def fadeIn(rateI):
	volI = 0.0
	while volI < 1:
		volI += 0.01
		volI = round(volI, 2)
		time.sleep(rateI)
#		pygame.mixer.music.set_volume(volI)	# This needs to be changed to the OMXWrapper API
		print(colored('Fading in: ', 'green'), volI, end='\r')
		sys.stdout.flush()
   
print(colored("Trigger Distance is set to: ", 'green'), colored(triggerDistance, 'green'))

# Take three distance measurements and average them. 
# Has self-ping error detection written into this function to prevent potential contamination with an erroneous reading.
def distance_average():
	div = 0
	c1 = get_distance()
	if c1 <= nearDistance:
		print("Self-ping while averaging. 1.")
		d1 = 0
		div = 0 
	else:
	  d1 = c1
	  div += 1

	c2 = get_distance()
	if c2 <= nearDistance:
		print("Self-ping while averaging. 2.")  
		d2 = 0
		div = 0
	else:
		d2 = c2
		div += 1

	c3 = get_distance()
	if c3 <= nearDistance:
		print("Self-ping while averaging. 3.")
		d3 = 0
		div = 0
	else:
		d3 = c3
		div += 1
	
	if div == 0:
	   return -5

	avgDist = d1 + d2 + d3
	
	avgDist = avgDist / 3
 
	avgDist = round(avgDist, 2)

	return avgDist

def smoothDistance():
	sd1 = get_distance()
	time.sleep(1)
	sd2 = get_distance()
	time.sleep(1)
	sd3 = get_distance()
	time.sleep(1)

	smoothD = sd1 + sd2 + sd3
	smoothD = smoothD / 3
	smoothD = round(smoothD, 2)

	return smoothD

try: 

	while True:

		logicDistance = distance_average()	# Single function call for control flow

		if logicDistance == 1000:
			print(colored("Sensor Error", 'red'))

		elif logicDistance <= nearDistance:
			print(colored("Sensor Self Ping Detected", "red"))
		
		elif logicDistance == -5:
			print(colored("Self ping throughout averaging. Retrying...", "red"))

		elif logicDistance < triggerDistance:    
			print ("Distance : ", logicDistance, "cm" , colored(" | Resuming Audio", 'green'))
			if rewind_counter > 30:
				rewind_counter = 0
			#	pygame.mixer.music.play(-1)	# This needs to be changed to the OMXWrapper API
				print(colored('Sampling target distance over 3 seconds. Please wait...', 'green'))
			else: 
			#	pygame.mixer.music.unpause()	# This needs to be changed to the OMXWrapper API
				fadeIn(0.02)
				print(colored('Fade in complete.', 'green'))
				rewind_counter = 0
				print("Target detected at  ", logicDistance, " cm")
				print(colored('Sampling target distance over 3 seconds. Please wait...', 'green'))
			while smoothDistance() < triggerDistance:
				print(colored('Current distance:', 'green'),distance_average(),' cm',end='\r')
				sys.stdout.flush()
				continue
			else:
				fadeOut(0.02)
				pygame.mixer.music.pause()	# This needs to be changed to the OMXWrapper API
				print(colored('Fade out complete.', 'green'))
				pygame.mixer.music.set_volume(1.0)	# This needs to be changed to the OMXWrapper API
		else:
			print ("Distance : ", logicDistance, "cm", colored(" | Audio Paused", "yellow"))
			rewind_counter += 1
			print(colored("Elapsed time since last playback reset: ", "yellow"), rewind_counter, colored("seconds", "yellow"))
			time.sleep(1)            
		
except KeyboardInterrupt:
	print(colored("Cleaning GPIO...", "yellow"))
	GPIO.cleanup()
	print(colored("OK", "green"))
	print(colored("Quiting OMXPlayer...", "yellow"))
	player.quit()	# Kill the `omxplayer` process gracefully.
	print(colored("OK", "green"))
	print(colored("Exiting...", "red"))
