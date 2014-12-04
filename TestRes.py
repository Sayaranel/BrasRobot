#!/usr/bin/env python

import socket

TCP_IP = '192.168.42.1'
TCP_PORT = 11000
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

conn, addr = s.accept()
print 'Connection address:', addr
while 1:
	data = conn.recv(BUFFER_SIZE)
	#if not data: break
	if data[0]=='a': print "Haut-Gauche"
	elif data[0]=='b': print "Haut-Droite"
	elif data[0]=='d': print "Bas-Gauche"
	elif data[0]=='e': print "Bas-Droite"
	elif data[0]=='x': print "Coupure onnection"
	elif not data:
		print "Coupure onnection"
		break
	else: print "Data received ", data
	#conn.send(data)  # echo
conn.close()
