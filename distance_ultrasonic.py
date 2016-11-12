from __future__ import print_function
from omxplayer import OMXPlayer
import RPi.GPIO as GPIO
import time, sys
from termcolor import colored
import pygame

trig = 23
echo = 24
triggerDistance = 60
nearDistance = 2
clipDistance = 300
rewind_counter = 0

GPIO.setwarnings(False)
GPIO.setmode (GPIO.BCM)
GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)

pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=4096)
pygame.mixer.music.load("/home/pi/Desktop/lucky_charms.ogg")
pygame.mixer.music.set_volume(0)

OMXlaunchParams = ['--no-osd', '--loop']
player = OMXPlayer('/home/pi/Desktop/Marie.mp4', args=OMXlaunchParams)

pygame.mixer.music.play()
player.play()

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

	if distance > clipDistance:
		return clipDistance

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
	   return -5

	if d1 > 500 or d2 > 500 or d3 > 500:	# Prevent averaging contamination with error codes. 
		return -4	# Return averaging error.

	avgDist = d1 + d2 + d3
	
	avgDist = avgDist / 3
 
	avgDist = round(avgDist, 2)

	return avgDist

def sampler(samples):
	sampleL = []
	err = 0
	for i in range(0, samples):
		sdist = get_distance()
		if sdist != 1000:
			sampleL.append(sdist)
		else:
			err += 1
	if len(sampleL) == 0:
		print ("Rapid averaging failed.")
	else:
		sDist = (sum(sampleL) / len(sampleL))
		sDist = round(sDist, 2)
		print (err, " errors occured during rapid averaging.")
		return sDist
	
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

	if sd1 == 1000 or sd2 == 1000 or sd3 == 1000: # Prevent averaging contamination with error codes. 
		return -8	# Return smooth averaging error.

	return smoothD

try: 

	while True:
                if pygame.mixer.music.get_busy() == 0:
                        player.set_position(0)
                        pygame.mixer.music.play()

		logicDistance = sampler(20)

		if logicDistance == 1000:
			print(colored("Sensor Error", 'red'))

		elif logicDistance == -4:
			print(colored("Averaging failed due to sensor error.", "red"))

		elif logicDistance <= nearDistance:
			print(colored("Sensor Self Ping Detected", "red"))

		elif logicDistance == -5:
			print(colored("Self ping throughout averaging. Retrying...", "red"))

		elif logicDistance < triggerDistance:    
			print ("Distance : ", logicDistance, "cm" , colored(" | Resuming Audio", 'green'))
			fadeIn(0.02)
			print(colored('Fade in complete.', 'green'))
			rewind_counter = 0
			print("Target detected at  ", logicDistance, " cm")
			print(colored('Sampling target distance over 3 seconds. Please wait...', 'green'))
			while sampler(100) < triggerDistance:
				smoothcap = smoothDistance()
				if pygame.mixer.music.get_busy() == 0:
                                        player.set_position(0)
                                        pygame.mixer.music.play()
                		if smoothcap == -8:
					print(colored("Error Correction Triggered. Assuming trigger distance until next accurate reading.", "magenta"))
				else:
      					print(colored('Current distance:', 'green'),smoothDistance(),' cm',end='\r')
					sys.stdout.flush()
					continue
			else:
				print('\n')
				fadeOut(0.02)
				print(colored('Fade out complete.', 'green'))
		else:
			print ("Distance : ", logicDistance, "cm", colored(" | Audio Paused", "yellow"))
			rewind_counter += 1
			print(colored("Elapsed time since last playback : ", "yellow"), rewind_counter, colored("seconds", "yellow"))
		time.sleep(1)
		
except KeyboardInterrupt:
	GPIO.cleanup()
	print(colored("Exiting.", "red"))
