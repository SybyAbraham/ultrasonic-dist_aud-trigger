from __future__ import print_function
import alsaaudio
from termcolor import colored
import RPi.GPIO as GPIO
import time, sys

# Pretentious print statements
print("Proximity based audio using ALSA. Syby Abraham 2016.")
print("Loading...")

# Pin and varible assignments
trig = 23
echo = 26
triggerDistance = 60		# Trigger distance to trigger fades.
nearDistance = 2		# Will display a self-ping error if below this value.
rewind_counter = 0		# Counts number of times through the control flow.
m = alsaaudio.Mixer("PCM")
vol = 100

# Set volume to 100%
m.setvolume(100)

# Raspberry Pi GPIO Setup Stuff
GPIO.setwarnings(False)
GPIO.setmode (GPIO.BCM)
GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)

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
	for volO in range(100, -1, -1):
		m.setvolume(volO)
		time.sleep(rateO)
		print(colored('Fading out: ', 'green'), volO, end='\r')
		sys.stdout.flush()

def fadeIn(rateI):
	for volI in range(0, 101):
		m.setvolume(volI)
		time.sleep(rateI)
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

		# Single function call for control flow
		logicDistance = distance_average()

		# Errors
		if logicDistance == 1000:
			print(colored("Sensor Error", 'red'))

		elif logicDistance <= nearDistance:
			print(colored("Sensor Self Ping Detected", "red"))
		
		elif logicDistance == -5:
			print(colored("Self ping throughout averaging. Retrying...", "red"))

		# Actual control flow for distance triggered fades
		elif logicDistance < triggerDistance:    
			print ("Distance : ", logicDistance, "cm" , colored(" | Resuming Audio", 'green'))
			fadeIn(0.02)
			vol = 100
			print(colored('Sampling target distance over 3 seconds. Please wait...', 'green'))
			while smoothDistance() < triggerDistance:
				print(colored('Current distance:', 'green'),distance_average(),' cm',end='\r')
				sys.stdout.flush()
				continue
		elif vol == 0:
			continue
		else:
			fadeOut(0.02)
			vol = 0
			print(colored('Fade out complete.', 'green'))			
		
except KeyboardInterrupt:
	print(colored("Cleaning GPIO...", "yellow"))
	GPIO.cleanup()
	print(colored("OK", "green"))
	print(colored("Exiting...", "red"))
