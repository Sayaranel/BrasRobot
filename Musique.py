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

#2e methode de frappe
PosFrapM1=[250,350,420,480]
PosFrapM2=[350,340,310,300]
PosFrapM3=[350,340,390,420]
PosFrapM4=[430,440,440,490]
PosFrapM5=[550,500,580,540]
PosFrapM6=320
ValFrap=[50,60,40,60]
ValUp=[0,10,10,-10,+10,0]
M4securite = 620

PeriodeTempo=2

#PosVal1 pour 4 bouteilles, si cela suit les previsions, les positions paires ne sont jamais appellees
#	  | | |
#	0 1	2 3
#En principe le reste du code s adapte au tableau, meme si on en change le nombre d element

Partition=[]
NotesAJouer=[]
VerrouNAJ = threading.Lock()
VerrouFrappe = threading.Lock()


##Fin des parametres globaux et ou de comportement

def pause():
  sleep(0.01)

def Vitesse(Dep, Act, Cib, LastInc):
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
	while Actu!=Target:
		print "Pas egal"
		for i in range(0,6):
			Inc[i]=Vitesse(Dep[i],Actu[i],Target[i],Inc[i])
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
		Inc=Vitesse(Dep,Actu[Moteur-1],Cible,Inc)
		if Inc<0:
			Actu[Moteur-1]=Actu[Moteur-1]+max(Inc,-MaxInc)
		else:
			Actu[Moteur-1]=Actu[Moteur-1]+min(Inc,MaxInc)
		pwm.setPWM(channel[Moteur-1],0,Actu[Moteur-1])
		pause()
	print "Target reach"

def init(Channel,Target):
	for i in range(0,6):
		pwm.setPWM(Channel[i],0,Target[i])
	print "Init OK"	
	
#Fonctions jeu musique	

def Frappe(Note):
	global PosFrapM5
	global ValFrap
	global VerrouFrappe
	
	if VerrouFrappe.locked():
		VerrouFrappe.acquire()
	else: #Le else sert a couvrir le cas ou on commence a jouer afin de se mettre dans le temp (car au depart le lock sera forcement relache)
		VerrouFrappe.acquire()
		VerrouFrappe.acquire()
	pwm.setPWM(10,0,PosFrapM5[Note]-ValFrap[Note])
	sleep(0.22) #sera adapte
	pwm.setPWM(10,0,PosFrapM5[Note])
	
def ChgmtPos(PosInit,PosCible):
	global Actu
	global PosFrapM1
	global PosFrapM2
	global PosFrapM3
	global PosFrapM4
	global PosFrapM5
	global M4securite
	
	# if PosInit == -1:
		# CibleAll=[Actu[0],450,350,450,400,Actu[5]]
	# else:
		# #CibleAll=[PosFrapM1[PosInit]+ValUp[0],PosFrapM2[PosInit]+ValUp[1],PosFrapM3[PosInit]+ValUp[2],PosFrapM4[PosInit]+ValUp[3],M4securite,Actu[5]]
		# CibleAll=[PosFrapM1[PosInit],PosFrapM2[PosInit],PosFrapM3[PosInit],PosFrapM4[PosInit],M4securite,Actu[5]]
	
	# CommandControlAll(CibleAll)
	# #CibleAll=[PosFrapM1[PosCible]+ValUp[0],PosFrapM2[PosCible]+ValUp[1],PosFrapM3[PosCible]+ValUp[2],PosFrapM4[PosCible]+ValUp[3],M4securite,Actu[5]]
	# CibleAll=[PosFrapM1[PosCible],PosFrapM2[PosCible],PosFrapM3[PosCible],PosFrapM4[PosCible],M4securite,Actu[5]]
	# CommandControlAll(CibleAll)
	pwm.setPWM(10,0,M4securite)
	pwm.setPWM(8,0,550)
	pause()
	CibleAll=[PosFrapM1[PosCible],PosFrapM2[PosCible],PosFrapM3[PosCible],PosFrapM4[PosCible],M4securite,Actu[5]]
	CommandControlAll(CibleAll)
	pwm.setPWM(10,0,PosFrapM5[PosCible])
	Actu[4]=PosFrapM5[PosCible]

def JeuNote(Note):
	global PosFrapM1
	global Actu
	PreviousNote = -1
	
	for i in range (0,PosFrapM1.__len__()):
		if Actu[0]==PosFrapM1[i]:
			PreviousNote = i
	
	if Note < PosFrapM1.__len__() and Note >= 0:
		if PreviousNote == Note:
			pass
		else:
			ChgmtPos(PreviousNote,Note)
		Frappe(Note)
	else:
		print "Note incorrecte"
	
#Thread Musicien	
def LectureNote(Lettre):
	if Lettre=='a' :
		return 1
	elif Lettre=='b' :
		return 2
	elif Lettre=='c' :
		return 3
	elif Lettre=='d' :
		return 0
	else:
		print "Probleme de lecture d une note par le musicien"
		return 0

def Musicien(): ##Tourne en boucle la fonction jeu note en fonction du mode
	global Mode
	global NotesAJouer, VerrouNAJ
	while 1:
		if NotesAJouer:
			if NotesAJouer[0]=='s':
				if VerrouFrappe.locked():
					VerrouFrappe.acquire()
				else: #voir frappe
					VerrouFrappe.acquire()
					VerrouFrappe.acquire()
			else:
				JeuNote(LectureNote(NotesAJouer[0]))
			NotesAJouer.pop(0)
		
#Thread Metronome
def Metronome():
	global VerrouFrappe
	global NotesAJouer
	try: #Essaie d'autoriser la frappe
		if VerrouFrappe.locked():
			VerrouFrappe.release()
	except: #erreur au metronome
		print "erreur au metronome"
		
class MyRepeater(object):
    def __init__(self, interval, function):#, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = None
        self.kwargs     = None
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function()#*self.args, **self.kwargs)

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
				elif not(data.__len__()>1):
					print data.__len__()
					print "Data received ", data
				else:
					VerrouNAJ.acquire()
					NotesAJouer.append(data[0])
					VerrouNAJ.release()
			elif Mode =='y':
				if data[data.__len__()-1-1]=='z' or data[data.__len__()-1-1]=='x':
					datalist=list(data)
					print "a",datalist[datalist.__len__()-1]
					print "b",datalist[datalist.__len__()-1-1]
					print "c",datalist[datalist.__len__()-1-1-1]
					
					NextMode=datalist[datalist.__len__()-1-1]
					datalist.pop(datalist.__len__()-1)
					datalist.pop(datalist.__len__()-1)
					print "NextMode",NextMode
					Partition.extend(datalist)
					if NextMode=='z':
						VerrouNAJ.acquire()
						NotesAJouer=[] #On remplace les instruction musicales en cours par la partition
						NotesAJouer.extend(Partition)
						VerrouNAJ.release()
					Mode=NextMode
				else:
					datalist=list(data)
					Partition.extend(datalist)
			elif Mode =='z':
				if data[0]=='x' or data[0]=='y':
					VerrouNAJ.acquire() #On interrompt la lecture
					NotesAJouer=[]
					VerrouNAJ.release()
					Mode=data[0]
				if data[0]=='y':
					Partition=[]
					Mode= 'y'
				if not NotesAJouer:
					Mode='x'
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

#Lancement reseau #Ne lit pas deux partition de suite (semble lire seulement la premiere note) # ne sort pas du mode partition si recoit une seule note ensuite (necessite 2 notes -> erreur provient de l android)
Port=12500
#threadres=threading.Thread(target=FuncRes, args=(Port,0))
#threadres.start()

while (True):
	print("0) Commande souple d'un moteur\n")
	print("1) Commande souple de tous les moteurs\n")
	print("2) Commande brute de tous les moteurs\n")
	print("3) Pince\n")
	print("4) Sequence exemple\n")
	print("5) Jouer une note demandee\n")
	print("6) PosInit\n")
	print("7) Encoder une partition\n")
	
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
		CommandControlUnique(6,PosFrapM6)
	elif(choix==4):
		VerrouFrappe.acquire()
		JeuNote(1)
		JeuNote(1)
		JeuNote(3)
		JeuNote(1)
		JeuNote(5)
		JeuNote(5)
		JeuNote(3)
		JeuNote(1)
	elif(choix==5):
		temp = input("Note a jouer ?")
		JeuNote(temp)
	elif(choix==6):
		valeur=[400,450,350,450,400,400]
		CommandControlAll(valeur)
	elif(choix==7):
		Part="abc"
		print "NAJ :", NotesAJouer
		Part = raw_input("Encode la partition (abc) :")#nb : input evalue ce qui est rentre comme un code python. Il tenterait alors d executer le string comme si c etait une commande
		VerrouNAJ.acquire()
		NotesAJouer=[] #On remplace les instruction musicales en cours par la partition
		NotesAJouer.extend(Part)
		VerrouNAJ.release()
		print "NAJ :", NotesAJouer
		while NotesAJouer:
			pass
		#On remet au repos
		valeur=[400,450,350,450,400,400]
		CommandControlAll(valeur)
	else:
		threadres.stop() #Faudra faire le code pour que cela se termine proprement http://python.developpez.com/faq/?page=Thread
		Metronome.stop()
		Musicien.stop()
		break