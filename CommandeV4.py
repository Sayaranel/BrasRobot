#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM
import time
#import numpy as np
from time import sleep

# ===========================================================================
# Example Code
# ===========================================================================

# Initialise the PWM device using the default address
# bmp = PWM(0x40, debug=True)
pwm = PWM(0x40, debug=True)

servoMin = 150  # Min pulse length out of 4096
servoMax = 600  # Max pulse length out of 4096

actu=[400,450,350,450,400,400]  #actual value of the impulsion of each servo
valeur = actu					#value to reach (initialized at actu)
channel=[1,2,3,4,5,6]			#number of the pin
pwm.setPWMFreq(60)                        # Set frequency to 60 Hz
cible = 0


def pause():
  sleep(0.01)
def setServoPulse(channel, pulse):
  pulseLength = 1000000                   # 1,000,000 us per second
  pulseLength /= 60                       # 50 Hz
  print "%d us per period" % pulseLength
  pulseLength /= 4096                     # 12 bits of resolutioni

  print "%d us per bit" % pulseLength
  pulse *= 1000
  pulse /= pulseLength
  #pwm.setPWM(channel, 0, pulse)

def TestEgList(A,B,nbr):
	Counter=0
	for i in range (0,nbr-1):
		if A[i]==B[i]:
			Counter = Counter +1
	
	if(Counter==nbr):
		return True
	else:
		return False

def Vitesse(Dep, Act, Cib, LastInc, MaxInc):
	Inc = 0
	if(Act!=Cib):
		if(Dep<Cib):
			if(Act <(Dep+((Cib-Dep)/2))):
				Inc=LastInc+1
			else:
				Inc=LastInc-1
				if(Inc<1):
					Inc=1
				if(Act+Inc>Cib):
					Inc=Cib-Act
		else:
			if(Act >(Dep-((Dep-Cib)/2))):
				Inc=LastInc-1
			else:
				Inc=LastInc+1
				if(Inc>(-1)):
					Inc=-1
				if(Act+Inc<Cib):
					Inc=Cib-Act
	return Inc
	
def CommandControlAll(Actu,Target):
	Dep=[Actu[0],Actu[1],Actu[2],Actu[3],Actu[4],Actu[5]]
	Inc=[0,0,0,0,0,0]
	MaxInc=[10,10,10,10,10,10]
	while(TestEgList(Actu,Target,6)==False):
		for i in range(0,5):
			Inc[i]=Vitesse(Dep[i],Actu[i],Target[i],Inc[i],MaxInc[i])
			if Inc<0:
				Actu[i]=Actu[i]+max(Inc[i],-MaxInc[i])
			else:
				Actu[i]=Actu[i]+min(Inc[i],MaxInc[i])
			pwm.setPWM((i+1)*2,0,Actu[i])
		pause()
	print "Target reach"
   
def CommandControlUnique(Channel,Actu,Target):
	Dep=Actu
	Inc=0
	MaxInc=10
	while(Actu!=Target):
		Inc=Vitesse(Dep,Actu,Target,Inc,MaxInc)
		if Inc<0:
			Actu=Actu+max(Inc,-MaxInc)
		else:
			Actu=Actu+min(Inc,MaxInc)
		pwm.setPWM(Channel,0,Actu)
		print "Actu %d" %Actu
		pause()
	print "Target reach"
 

def init(Channel,Target):
	for i in range(0,6):
		a=2*Channel[i]
		b=Target[i]
		pwm.setPWM(a,0,b)
	print "Init OK"

init(channel,actu) #To initialize the servos

while (True):
  #cible = input("Element a controler :")
  choix=input("Voulez-vous controler tous les moteurs (1) ou un a la fois (0) (2 = un brute): ")
  if(choix==1):
    for i in range(0,6):
	  valeur[i] = input("Prochaine valeur a atteindre du moteur %d : " %channel[i])
    CommandControlAll(actu,valeur)
  else:
	if(choix==0):
		cible = input("Element a controler : ")
		temp = input("Prochaine valeur a atteindre du moteur %d : " %cible)
		a = actu[cible-1]
		CommandControlUnique(2*cible,a,temp)
		valeur[cible-1]=temp
	else:
		cible = input("Element a controler : ")
		temp = input("Prochaine valeur a atteindre du moteur %d : " %cible)
		pwm.setPWM(2*cible,0,temp)
		valeur[cible-1]=temp
  #setServoPulse(0,valeur)  
  actu=valeur
  #pwm.setPWM(cible,0,valeur)






#  # Change speed of continuous servo on channel O
#  pwm.setPWM(0, 0, servoMin)
#  time.sleep(1)
#  pwm.setPWM(0, 0, servoMax)
#  time.sleep(1)


