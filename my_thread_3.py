#!/usr/bin/python

# start two threads each one executing a function every interval in seconds 
# uses global variables shared between threads

# ------------------------------------------------------
# MyRepeater launches a thread calling a user function
 
from threading import Timer 
import time;  # This is required to include time module.

class MyRepeater(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
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
	
from time import sleep

# ------------------------------------------------------
# Functions be executed by the repeater
 	
glob_count = 1 

def myFunction(name,number): 
	global glob_count
	print "\t %d: Hello %d %s!" % (number, glob_count, name)  
	glob_count+=1 

def myTime(name,number): 
	global glob_count
	print "\t %d: Hello %d %f %s!" % (number, glob_count, time.time(), name)  

 	
# ------------------------------------------------------
# MAIN  
 
print "Start..."

# it auto-starts, no need of rt.start()
myr1 = MyRepeater(0.01, myTime, "Time", 1) # call myFunction every 10ms 
myr2 = MyRepeater(1, myFunction, "World", 2) # call myFunction every 1s 

try:
    sleep(5) # your long-running job goes here...
	
finally:
    myr1.stop() # better in a try/finally block to make sure the program ends!
    myr2.stop() # better in a try/finally block to make sure the program ends!

print "Bye %d ..."  % glob_count
