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
	if not data:
		print "Coupure connection"
		break
	else: print "Data received ", data
	#conn.send(data)  # echo
conn.close()
