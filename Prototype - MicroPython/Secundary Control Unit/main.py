from machine import Pin, UART
from utime import sleep
#from blink import blink_led
from uart1pico2 import uart1pico2
from RelayMOSFET import opengate, closegate

pin = Pin("LED", Pin.OUT, value=0)
gate = Pin(5, Pin.OUT, value=0)  # 4 as output to control a gate (initially low)
uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9), timeout=1000) #define the tx, rx pins and baudrate for UART 0 of pico

pin.toggle()
sleep(.1)
pin.toggle()
sleep(.1)
pin.toggle()
sleep(.1)
pin.toggle()

closegate(gate)
while True:
    if uart1pico2(uart):
        opengate(gate)

    sleep(0.5)

