# Distance/Proximity based Audio Track Player

Uses PyGame to play an audio track based on distance using an HC-SR04 ultrasonic distance sensor.

Features
--------------------------------
-Play a track when set distance(triggerDistance) is reached. Pause when distance is higher than the set trigger distance. 

-Continue playing from previous position if trigger distance is reached again within 30 seconds of losing it. 

-Hold position of the audio track for 30 seconds and then seek back to the start of the track. 
