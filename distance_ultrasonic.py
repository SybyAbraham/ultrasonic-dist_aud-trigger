from __future__ import print_function
from omxplayer import OMXPlayer
import RPi.GPIO as GPIO
import time, sys
from termcolor import colored
import pygame

# Pin and variable assignments
trig = 23
echo = 24
triggerDistance = 60		# Trigger distance to trigger fades.
nearDistance = 2		# Will display a self-ping error if reading falls below this value.
clipDistance = 300		# Clip the reading to this value if reading falls above this value.
rewind_counter = 0		# Counts the number of times the code has passed through the control flow. 

# Pretentious print statements
print(colored("Proximity based audio fader using PyGame. Syby Abraham 2016.", "magenta"))
print(colored("Loading...", "magenta"))
print(colored("Trigger Distance is set to: ", 'green'), colored(triggerDistance, 'magenta'))

# Raspberry Pi GPIO setup stuff
GPIO.setwarnings(False)
GPIO.setmode (GPIO.BCM)
GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)

# Initialize PyGame
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=4096)
pygame.mixer.music.load("/home/pi/Desktop/FILE.EXT")
pygame.mixer.music.set_volume(0)

# Initialize OMXPlayer
OMXlaunchParams = ['--no-osd', '--loop']	# Launch OMXPlayer with no OSD and loop the video.
player = OMXPlayer('/home/pi/Desktop/FILE.EXT', args=OMXlaunchParams)

# Play both audio and video
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

# PyGame fade out function
def fadeOut(rateO):
	volO = 1.0
	while volO > 0:
		volO -= 0.01
		volO = round(volO, 2)
		time.sleep(rateO)
		pygame.mixer.music.set_volume(volO)
		print(colored('Fading out: ', 'green'), volO, end='\r')
		sys.stdout.flush()
		
# PyGame fade in function	
def fadeIn(rateI):
	volI = 0.0
	while volI < 1:
		volI += 0.01
		volI = round(volI, 2)
		time.sleep(rateI)
		pygame.mixer.music.set_volume(volI)
		print(colored('Fading in: ', 'green'), volI, end='\r')
		sys.stdout.flush()
		
# Sampling and averaging function   
# Measures and puts the measurement into a list and then averages the values in the list for a final measurement output. 
# Takes two arguments "samples" and "time", which sets the number of samples to take and wait time between each sample. 
def sampler(samples, time):
	sampleL = []
	err = 0
	for i in range(0, samples):
		sdist = get_distance()
		if sdist != 1000 and sdist > nearDistance:
			sampleL.append(sdist)
			time.sleep(time)
		else:
			err += 1
			time.sleep(time)
	if len(sampleL) == 0:
		print ("Rapid averaging failed.")
		return 1000
	else:
		sDist = (sum(sampleL) / len(sampleL))
		sDist = round(sDist, 2)
		print (err, " errors occured during rapid averaging.")
		return sDist

try: 

	while True:
		# If PyGame audio track has ended, restart the audio track and rewind the video back to start. 
                if pygame.mixer.music.get_busy() == 0:
                        player.set_position(0)
                        pygame.mixer.music.play()
			
		# Take twenty distance measurements without waiting between measurements and average them.
		logicDistance = sampler(20) 

		if logicDistance == 1000:
			print(colored("Sensor Error", 'red'))

		elif logicDistance <= nearDistance:
			print(colored("Sensor Self Ping Detected", "red"))

		elif logicDistance < triggerDistance:    
			print ("Distance : ", logicDistance, "cm" , colored(" | Resuming Audio", 'green'))
			fadeIn(0.02)
			print(colored('Fade in complete.', 'green'))
			rewind_counter = 0
			print("Target detected at  ", logicDistance, " cm")
			print(colored('Sampling target distance over 3 seconds. Please wait...', 'green'))
			while sampler(100) < triggerDistance:
				smoothcap = sampler(100)
				if pygame.mixer.music.get_busy() == 0:
                                        player.set_position(0)
                                        pygame.mixer.music.play()
                		if smoothcap == 1000:
					print(colored("Error Correction Triggered. Assuming trigger distance until next accurate reading.", "magenta"))
				else:
      					print(colored('Current distance:', 'green'),smoothcap,' cm',end='\r')
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
