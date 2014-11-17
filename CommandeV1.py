#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM
import time
from time import sleep

# ===========================================================================
# Example Code
# ===========================================================================

# Initialise the PWM device using the default address
# bmp = PWM(0x40, debug=True)
pwm = PWM(0x40, debug=True)

servoMin = 150  # Min pulse length out of 4096
servoMax = 600  # Max pulse length out of 4096
def pause():
  sleep(0.005)
def setServoPulse(channel, pulse):
  pulseLength = 1000000                   # 1,000,000 us per second
  pulseLength /= 60                       # 50 Hz
  print "%d us per period" % pulseLength
  pulseLength /= 4096                     # 12 bits of resolutioni

  print "%d us per bit" % pulseLength
  pulse *= 1000
  pulse /= pulseLength
  pwm.setPWM(channel, 0, pulse)

def CommandControl(Channel,Temp,Target):
  while (Target!=Temp):
   if(Target<Temp):
     Temp=Temp-1
     pause()
   else:
     Temp=Temp+1
     pause()
   pwm.setPWM(Channel,0,Temp)
  print "Target reach"

Actual = array([1,1,1,1,1,1])
Actual = Actual*400  
Temp = 400

pwm.setPWMFreq(60)                        # Set frequency to 60 Hz
valeur = 0
cible = 0
i = 0

for i in range(0,15):
  CommandControl(i,200,400)
  Actual=400
  i=i+1
#for i in range(0,15):
 # pwm.setPWM(i,0,353)
  #i=i+1

while (True):
  cible = input("Element a controler :")
  valeur = input("Prochaine valeur a atteindre (246-423-600:")
  #setServoPulse(0,valeur)
  CommandControl(cible,Actual[cible],valeur)
  Actual[cible]=valeur
  #pwm.setPWM(cible,0,valeur)






#  # Change speed of continuous servo on channel O
#  pwm.setPWM(0, 0, servoMin)
#  time.sleep(1)
#  pwm.setPWM(0, 0, servoMax)
#  time.sleep(1)


