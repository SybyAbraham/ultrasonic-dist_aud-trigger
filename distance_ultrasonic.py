from __future__ import print_function
import RPi.GPIO as GPIO
import time, sys
from termcolor import colored
import pygame

pygame.mixer.init()
pygame.mixer.music.load("/home/pi/Desktop/FILENAME.EXT")
pygame.mixer.music.play(-1)
pygame.mixer.music.pause()

GPIO.setmode (GPIO.BCM)

trig = 23
echo = 26
led = 24
triggerDistance = 60
nearDistance = 2
rewind_counter = 0

GPIO.setup(trig, GPIO.OUT)
GPIO.setup(led, GPIO.OUT)    
GPIO.setup(echo, GPIO.IN)
GPIO.setwarnings(False)

def ledBlink():
	GPIO.output(led, True)
	time.sleep(0.3)
	GPIO.output(led, False)

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
		pygame.mixer.music.set_volume(volO)
		print(colored('Fading out: ', 'green'), volO, end='\r')
		sys.stdout.flush()
	
def fadeIn(rateI):
	volI = 0.0
	while volI < 1:
		volI += 0.01
		volI = round(volI, 2)
		time.sleep(rateI)
		pygame.mixer.music.set_volume(volI)
		print(colored('Fading in: ', 'green'), volI, end='\r')
		sys.stdout.flush()
   
print(colored("Trigger Distance is set to: ", 'green'), colored(triggerDistance, 'green'))

def distance_average():
	c1 = get_distance()
	div = 0
	if c1 < nearDistance:
		print("Self-ping while averaging. 1.")
		d1 = 0
		div = 0 
	else:
	  d1 = c1
	  div += 1
	c2 = get_distance()
	if c2 < nearDistance:
		print("Self-ping while averaging. 2.")  
		d2 = 0
		div = 0
	else:
		d2 = c2
		div += 1
	c3 = get_distance()
	if c3 < nearDistance:
		print("Self-ping while averaging. 3.")
		d3 = 0
		div = 0
	else:
		d3 = c3
		div += 1
	
	if div == 0:
	   return (nearDistance)

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

	logicDistance = distance_average()

		if logicDistance == 1000:
			print(colored("Sensor Error", 'red'))

		elif logicDistance <= nearDistance:
			print(colored("Sensor Self Ping Detected", "red"))

		elif logicDistance < triggerDistance:    
			print ("Distance : ", logicDistance, "cm" , colored(" | Resuming Audio", 'green'))
			if rewind_counter > 30:
				rewind_counter = 0
				pygame.mixer.music.play(-1)
				GPIO.output(led, True)
				print(colored('Sampling target distance over 3 seconds. Please wait...', 'green'))
			else: 
				GPIO.output(led, True)
				pygame.mixer.music.unpause()
				fadeIn(0.02)
				print(colored('Fade in complete.', 'green'))
				rewind_counter = 0
				print("Target detected at  ", logicDistance, " cm")
				print(colored('Sampling target distance over 3 seconds. Please wait...', 'green'))
			while smoothDistance() < triggerDistance:
				ledBlink()
				print(colored('Current distance:', 'green'),distance_average(),' cm',end='\r')
				sys.stdout.flush()
				continue
			else:
				print('\n')
				fadeOut(0.02)
				GPIO.output(led, False)
				pygame.mixer.music.pause()
				print(colored('Fade out complete.', 'green'))
				pygame.mixer.music.set_volume(1.0)
		else:
			print ("Distance : ", logicDistance, "cm", colored(" | Audio Paused", "yellow"))
			rewind_counter += 1
			print(colored("Elapsed time since last playback reset: ", "yellow"), rewind_counter, colored("seconds", "yellow"))
			time.sleep(1)            
		
except KeyboardInterrupt:
	GPIO.cleanup()
	print(colored("Exiting.", "red"))
