from machine import Pin
from utime import sleep

pin = Pin("LED", Pin.OUT)

def opengate(gate):
    
    pin(1)
    gate.value(1)   # MOSFET ein

def closegate(gate):

    pin(0)
    gate.value(0)