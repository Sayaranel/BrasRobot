#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM
import time
from time import sleep

#blabla
import socket
import threading

def FuncRes(Port,nothing):
	
	TCP_IP = '192.168.42.1'
	TCP_PORT = Port
	BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((TCP_IP, TCP_PORT))
	s.listen(1)
	
	while 1:
		conn, addr = s.accept()
		print 'Connection address:', addr
		while 1:
			data = conn.recv(BUFFER_SIZE)
			#if not data: break
			if not data:
				print "Coupure connection"
				break
			if data[0]=='a': print "Haut-Gauche"
			elif data[0]=='b': print "Haut-Droite"
			elif data[0]=='d': print "Bas-Gauche"
			elif data[0]=='e': print "Bas-Droite"
			else: print "Data received ", data
	#conn.send(data)  # echo
	conn.close()


# ===========================================================================
# Musique (sans thread timer)
# ===========================================================================

#Parametres generaux et/ou globaux
ServoMin=[130,230,230,180,145,200]
ServoMax=[630,690,580,630,660,660] # Min pulse length out of 4096
Init=[400,450,350,450,400,400]  #actual value of the impulsion of each servo
channel=[2,4,6,8,10,12]			#where pins are plugged
PWMFreq = 60					# Set frequency to 60 Hz           

Actu=[0,0,0,0,0,0]

#Parametres musiquaux
PosFrap=[400,450,350,450,400,320]
PosPivot=[400,450,350,450,400,320]
PosVal1=[150,0,250,0,350,0,450,0,550]
#PosVal1 pour 4 bouteilles, si cela suit les previsions, les positions paires ne sont jamais appellees
#		|		|		|		|
#	0	1	2	3	4	5	6	7	8
#En principe le reste du code s adapte au tableau, meme si on en change le nombre d element

VarFrap=100
	
def pause():
  sleep(0.01)
 
def TestEgList(A,B,nbr):
	print "A0 %d B0 %d" %(A[0],B[0])
	Counter=0
	for i in range (0,nbr):
		if A[i]==B[i]:
			print "TrueInt %d A %d B %d" %(Counter,A[i],B[i])
			Counter = Counter +1
	
	if(Counter==nbr):
		print "True %d" %Counter
		return True
	else:
		print "False"
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
	
def CommandControlAll(Target):
	global channel
	global Actu
	Dep=[Actu[0],Actu[1],Actu[2],Actu[3],Actu[4],Actu[5]]
	Inc=[0,0,0,0,0,0]
	MaxInc=[10,10,10,10,10,10]
	print "ActuAvtTest0 %d TrgtAvtTest0 %d" %(Actu[0],Target[0])
	while(TestEgList(Actu,Target,6)==False):
		print "Pas egal"
		for i in range(0,6):
			Inc[i]=Vitesse(Dep[i],Actu[i],Target[i],Inc[i],MaxInc[i])
			if Inc<0:
				Actu[i]=Actu[i]+max(Inc[i],-MaxInc[i])
			else:
				Actu[i]=Actu[i]+min(Inc[i],MaxInc[i])
			pwm.setPWM(channel[i],0,Actu[i])
			print "Mot %d Actu %d Cib %d" %(i+1,Actu[i],Target[i])
		pause()
	print "Target reach"
   
def CommandControlUnique(Moteur,Cible):
	global Actu
	global channel
	Dep=Actu[Moteur-1]
	Inc=0
	MaxInc=10
	while(Actu[Moteur-1]!=Cible):
		Inc=Vitesse(Dep,Actu[Moteur-1],Cible,Inc,MaxInc)
		if Inc<0:
			Actu[Moteur-1]=Actu[Moteur-1]+max(Inc,-MaxInc)
		else:
			Actu[Moteur-1]=Actu[Moteur-1]+min(Inc,MaxInc)
		pwm.setPWM(channel[Moteur-1],0,Actu[Moteur-1])
		#print "Actu %d" %Actu
		pause()
	print "Target reach"

def init(Channel,Target):
	for i in range(0,6):
		pwm.setPWM(Channel[i],0,Target[i])
	print "Init OK"

#Fonctions jeu musique	
	
def Frappe(direction):
	global PosFrap
	global VarFrap
	global Actu
	if direction=="gauche":
		CibleSeul=PosFrap[4]-VarFrap #Pas sur pour le -, sera p tet plus
	else:
		CibleSeul=PosFrap[4]+VarFrap #Pas sur pour le +, sera p tet -
	#Pos du futur timer
	CommandControlUnique(5,CibleSeul) #Coup rapide ?
	CommandControlUnique(5,PosFrap[4]) #Retour aussi rapide pour frappe nette ? Calculer le temps necessaire pour toucher pour revenir immediatement ?
	
def ChgmtPos(PosCible):
	global Actu
	global PosPivot
	global PosFrap
	global PosVal1
	CibleAll=[Actu[0],PosPivot[1],PosPivot[2],PosPivot[3],PosPivot[4],PosPivot[5]]
	CommandControlAll(CibleAll)
	CommandControlUnique(1,PosVal1[PosCible])
	CibleAll=[Actu[0],PosFrap[1],PosFrap[2],PosFrap[3],PosFrap[4],PosFrap[5]]
	CommandControlAll(CibleAll)

def JeuNote(Note):
	global PosVal1
	Pos=-1 #sert de valeur par defaut
	for i in range (0,len(PosVal1)):
		if Actu[0]==PosVal1[i]:
			Pos=i
			break
	if Pos+1==Note:
		Frappe("droite")
	elif Pos-1==Note:
		Frappe("gauche")
	elif Pos<=Note:
		ChgmtPos(Note-1)
		Frappe("droite")
	else:
		ChgmtPos(Note+1)
		Frappe("gauche")
##Main

# Initialise the PWM device using the default address
pwm = PWM(0x40, debug=True)
pwm.setPWMFreq(PWMFreq)  

init(channel,Init) #To initialize the servos
Actu=Init
valeur=Init

#Blabla
Port=11000
threadres=threading.Thread(target=FuncRes, args=(Port,0))
threadres.start()

while (True):
	print("0) Commande souple d'un moteur\n")
	print("1) Commande souple de tous les moteurs\n")
	print("2) Commande brute de tous les moteurs\n")
	print("3) Musiques ! (exemple)\n")
	
	choix=input("Votre choix ?")
	if(choix==0):
		cible = input("Element a controler")
		temp = input("Prochaine valeur a atteindre du moteur %d (%d - %d): " %(cible,ServoMin[cible-1],ServoMax[cible-1]))
		CommandControlUnique(cible,temp)
	elif(choix==1): #elif -> "else if"
		for i in range(0,6):
			valeur[i] = input("Prochaine valeur a atteindre du moteur %d (%d - %d) : " %(i+1,ServoMin[i],ServoMax[i]))
		print "Actu1 %d" %Actu[0]
		CommandControlAll(valeur)
	elif(choix==2):
		cible = input("Element a controler : ")
		temp = input("Prochaine valeur a atteindre du moteur %d (%d - %d): " %(cible,ServoMin[cible-1],ServoMax[cible-1]))
		pwm.setPWM(2*cible,0,temp)
		actu[cible-1]=temp
	elif(choix==3):
		print("Preparez vous a mettre la baguette\n")
		sleep(1)
		CommandControlUnique(6,ServoMax[5])
		print("Mettez la baguette\n")
		sleep(2)
		CommandControlUnique(6,PosPivot[5])
		print("Attente des instructions\n")
		
	else:
		threadres.join()
		break