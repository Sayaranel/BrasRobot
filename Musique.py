#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM
import time
from time import sleep
from threading import Timer 
import time
import socket
import threading

# ===========================================================================
# Musique (avec thread timer)
# ===========================================================================

#Parametres generaux et/ou globaux
ServoMin=[130,230,230,180,145,200]
ServoMax=[630,690,580,630,660,660] # Min pulse length out of 4096
Actu=[400,450,350,450,400,400]  #actual value of the impulsion of each servo
channel=[2,4,6,8,10,12]			#where pins are plugged
PWMFreq = 60					# Set frequency to 60 Hz           

valeur=[0,0,0,0,0,0]

Mode = 'x' #x = commande directement, y = ecriture partition

#Parametres musiquaux
PosPivot=[0,420,308,450,370,320] #Le 0 correspond a une des PosVal1
PosVal1=[130,0,370,0,430,0,600]
PosFrapM2=[360,0,350,0,350,0,360]
PosFrapM3=[270,0,308,0,308,0,270]
PosFrapM4=[450,0,450,0,450,0,450]
PosFrapM5=[400,0,370,0,400,0,400]
PosFrapM5Dr=[400,0,335,0,350,0,400] ##Bouger 2 moteurs pour la frappe ?
PosFrapM5Ga=[400,0,405,0,435,0,400]
PosFrapM6=320

PeriodeTempo=5

#PosVal1 pour 4 bouteilles, si cela suit les previsions, les positions paires ne sont jamais appellees
#		|		|		|	
#	X	1	2	3	4	5	X
#En principe le reste du code s adapte au tableau, meme si on en change le nombre d element

Partition=[]
NotesAJouer=[]
VerrouNAJ = threading.Lock()
VerrouFrappe = threading.Lock()


##Fin des parametres globaux et ou de comportement

def pause():
  sleep(0.01)

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
	for i in range(0,6):
		print "ActuAvtTest%d %d TrgtAvtTest%d %d" %(i,Actu[i],i,Target[i])
	while Actu!=Target:#TestEgList(Actu,Target,6)==False): #Actu==Target marche ptet
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
	
def Frappe(Pos,direction):
	global PosFrapM5
	global PosFrapM5Dr
	global PosFrapM5Ga
	global VerrouFrappe
	
	VerrouFrappe.acquire()
	if direction=="gauche": ##Modif ici
		pwm.setPWM(10,0,PosFrapM5Ga[Pos])
	else:
		pwm.setPWM(10,0,PosFrapM5Dr[Pos])
	sleep(0.3) #sera adapte
	pwm.setPWM(10,0,PosFrapM5[Pos])
	
def ChgmtPos(PosCible):
	global Actu
	global PosPivot
	global PosFrapM2
	global PosFrapM3
	global PosFrapM4
	global PosFrapM5
	global PosFrapM5
	global PosFrapM5
	global PosVal1
	CibleAll=[Actu[0],PosPivot[1],PosPivot[2],PosPivot[3],PosPivot[4],Actu[5]]
	CommandControlAll(CibleAll)
	CommandControlUnique(1,PosVal1[PosCible])
	CibleAll=[Actu[0],PosFrapM2[PosCible],PosFrapM3[PosCible],PosFrapM4[PosCible],PosFrapM5[PosCible],Actu[5]]
	CommandControlAll(CibleAll)

def JeuNote(Note):
	global PosVal1
	global Actu
	
	if Note==1:
		if Actu[0]==PosVal1[2]:
			print "Frappe a gauche"
			Frappe(2,"gauche")
		else:
			print "Changement de position"
			ChgmtPos(2)
			print "Frappe a gauche"
			Frappe(2,"gauche")
	elif Note==PosVal1.__len__()-2:
		if Actu[0]==PosVal1[PosVal1.__len__()-3]:
			print "Deja en position"
			print "Frappe a droite"
			Frappe(PosVal1.__len__()-3,"droite")
		else:
			print "Changement de position"
			ChgmtPos(PosVal1.__len__()-3)
			print "Frappe a droite"
			Frappe(PosVal1.__len__()-3,"droite")	
	elif Actu[0]==PosVal1[Note-1]:
		print "Deja en position"
		print "Frappe a droite"
		Frappe(Note-1,"droite")
	elif Actu[0]==PosVal1[Note+1]:
		print "Deja en position"
		print "Frappe a gauche"
		Frappe(Note+1,"gauche")
	elif Actu[0]<PosVal1[Note-1]:
		print "Changement de position"
		ChgmtPos(Note-1)
		print "Frappe a droite"
		Frappe(Note-1,"droite")
	elif Actu[0]<PosVal1[Note-1]: #on respectera Actu[0]>PosVal1[Note-1] ou alors on sera dans une postion absurbe qui de toute facon tolere les commandes qui suivent
		print "Changement de position"
		ChgmtPos(Note+1)
		print "Frappe a gauche"
		Frappe(Note+1,"gauche")

def MusiqueInit():
	global PosPivot
	global PosVal1
	global Actu
	
	CibleAll=[Actu[0],450,350,450,Actu[4],Actu[5]]
	CommandControlAll(CibleAll)
	CibleAll=[360,PosPivot[1],PosPivot[2],PosPivot[3],PosPivot[4],Actu[5]]
	CommandControlAll(CibleAll)

	
#Thread Musicien	
def LectureNote(Lettre):
	if Lettre=='a' :
		NumNote=1
	elif Lettre=='b' :
		NumNote=3
	elif Lettre=='c' :
		NumNote=5
	else:
		print "Probleme de lecture d une note par le musicien"
		NumNote=1
	return NumNote

def Musicien(): ##Tourne en boucle la fonction jeu note en fonction du mode
	global Mode
	global NotesAJouer, VerrouNAJ
	
	if NotesAJouer:
		JeuNote(LectureNote(NotesAJouer[0]))
		NotesAJouer.pop(0)
		
#Thread Metronome
def Metronome():
	global VerrouFrappe
	global NotesAJouer
	try: #Essaie d'autoriser la frappe
		VerrouFrappe.release()
	except ThreadError: #si la frappe était déjà autorisée, capture l'erreur
		if NotesAJouer: #Si il y a des notes a jouer
			print"Thread error au niveau du metronome. Tempo trop rapide ?"
		
class MyRepeater(object):
    def __init__(self, interval, function):#, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        #self.args       = args
        #self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False	
	
#Reseau
def FuncRes(Port,nothing):
	global Mode
	global NotesAJouer, VerrouNAJ
	global Partition
	
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
			if not data:
				print "Coupure connection"
				break
			elif Mode =='x':
				if data[0]=='x':
					pass
				elif data[0]=='y':
					Partition=[]
					Mode= 'y'
				elif data[0]=='z':
					VerrouNAJ.acquire()
					NotesAJouer=[] #On remplace les instruction musicales en cours par la partition
					NotesAJouer.extend(Partition)
					VerrouNAJ.release()
					Mode = 'z'
				elif not(data.__len__()==1):
					print "Data received ", data
				else:
					VerrouNAJ.acquire()
					NotesAJouer.append(data[0])
					VerrouNAJ.release()
			elif Mode =='y':
				if Data[Data.__len__()-1]=='z' or Data[Data.__len__()-1]=='x':
					NextMode=Data[Data.__len__()-1]
					Data.pop(Data.__len__()-1)
					Partition.extend(Data)
					if NextMode=='z':
						VerrouNAJ.acquire()
						NotesAJouer=[] #On remplace les instruction musicales en cours par la partition
						NotesAJouer.extend(Partition)
						VerrouNAJ.release()
					Mode=NextMode
				else:
					Partition.extend(Data)
			elif Mode =='z':
				if data[0]=='x' or data[0]=='y':
					VerrouNAJ.acquire() #On interrompt la lecture
					NotesAJouer=[]
					VerrouNAJ.release()
					Mode=data[0]
			else:
				Mode == 'x'
	conn.close()
##Main

# Initialise the PWM device using the default address
pwm = PWM(0x40, debug=True)
pwm.setPWMFreq(PWMFreq)  

init(channel,Actu) #To initialize the servos

#Lancement du metronome et du musicien
Metro= MyRepeater(PeriodeTempo, Metronome) # call myFunction every Periode Tempo secondes
#Metro auto-start
Music= threading.Thread(target=Musicien)
Music.start()

#Lancement reseau
Port=11000
threadres=threading.Thread(target=FuncRes, args=(Port,0))
threadres.start()

while (True):
	print("0) Commande souple d'un moteur\n")
	print("1) Commande souple de tous les moteurs\n")
	print("2) Commande brute de tous les moteurs\n")
	print("3) Musiques ! (exemple)\n")
	print("4) Sequence exemple\n")
	print("5) Jouer une note demandee\n")
	
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
		Actu[cible-1]=temp
	elif(choix==3):
		print("Preparez vous a mettre la baguette\n")
		sleep(0.2)
		CommandControlUnique(6,ServoMax[5])
		print("Mettez la baguette\n")
		sleep(1)
		CommandControlUnique(6,PosPivot[5])
		sleep(1)
		MusiqueInit()
		print("Attente des instructions\n")
	elif(choix==4):
		MusiqueInit()
		print "En position initiale"
		JeuNote(1)
		sleep(1)
		JeuNote(1)
		sleep(1)
		JeuNote(3)
		sleep(1)
		JeuNote(1)
		sleep(1)
		JeuNote(5)
		sleep(1)
		JeuNote(3)
		sleep(1)
		JeuNote(1)
	elif(choix==5):
		temp = input("Note a jouer ?")
		JeuNote(temp)
	else:
		threadres.stop() #Faudra faire le code pour que cela se termine proprement http://python.developpez.com/faq/?page=Thread
		Metronome.stop()
		Musicien.stop()
		break