from __future__ import print_function
import RPi.GPIO as GPIO
import time, sys
from termcolor import colored
import pygame

pygame.mixer.init()
pygame.mixer.music.load("the_greatest.ogg")
pygame.mixer.music.play()
pygame.mixer.music.pause()

trig = 23
echo = 24
rewind_counter = 0
triggerDistance = 70
nearDistance = 2

GPIO.setmode (GPIO.BCM)


GPIO.setup(trig, GPIO.OUT)    
GPIO.setup(echo, GPIO.IN)
GPIO.setwarnings(False)

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

def fadeOut(rate):
    volO = 1.0
    while volO > 0:
			volO -= 0.01
			volO = round(volO, 2)
			time.sleep(rate)
			pygame.mixer.music.set_volume(volO)
			print(colored('Fading out: ', 'green'), volO, end='\r')
			sys.stdout.flush()
	
def fadeIn(rate):
    volI = 0.0
    while volI < 1:
			volI += 0.01
			volI = round(volI, 2)
			time.sleep(rate)
			pygame.mixer.music.set_volume(volI)
			print(colored('Fading in: ', 'green'), volI, end='\r')
			sys.stdout.flush()
   
print(colored("Trigger Distance is set to: ", 'green'), colored(triggerDistance, 'green'))

def distance_average():
    d1 = get_distance()
    d2 = get_distance()
    d3 = get_distance()

    avgdist = d1 + d2 + d3

    avgdist = avgdist / 3
 
    avgdist = round(avgdist, 2)

    return avgdist

time.sleep(0.1) # To prevent initial sensor error. 

try: 

    while True:

				logicDistance = distance_average()

        if logicDistance == 1000:
            print(colored("Sensor Error", 'red'))

        elif logicDistance < nearDistance:
            colored("Sensor Self Ping Detected", "red")

        elif logicDistance < triggerDistance:    
            print ("Distance : ", logicDistance, "cm" , colored(" | Resuming Audio", 'green'))
            if rewind_counter > 30:
                rewind_counter = 0
                pygame.mixer.music.play()
            else: 
                pygame.mixer.music.unpause()
								fadeIn(0.01)
								print(colored('Fade in complete.', 'green'))
								rewind_counter = 0
                print("Target detected at  ", logicDistance, " cm")
            while distance_average() < triggerDistance:
                continue
            else:
                fadeOut(0.01)
                pygame.mixer.music.pause()
								print(colored('Fade out complete.', 'green'))
								pygame.mixer.music.set_volume(1.0)
        else:
            print ("Distance : ", logicDistance, "cm", colored(" | Audio Paused", "yellow"))
            rewind_counter = rewind_counter+1
            print(colored("Elapsed time since last playback reset: ", "yellow"), rewind_counter, colored("seconds", "yellow"))
            time.sleep(1)
        
except KeyboardInterrupt:
    GPIO.cleanup()
