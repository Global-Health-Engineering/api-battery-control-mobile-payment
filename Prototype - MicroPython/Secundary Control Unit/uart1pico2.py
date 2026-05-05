from machine import Pin
from utime import sleep

pin = Pin("LED", Pin.OUT)

def uart1pico2(uart):

    if uart.any():
        pin.toggle()
        sleep(0.5)
        resp = uart.read().decode()
        sleep(0.1)
        pin.toggle()
        print(resp)
        if 'Hello from Pico! Open gate' in resp:
            uart.write(b'Hello from Pico! Gate is open\n')
            return True
        
        
    else:
        print('waiting...')
        pin.toggle()
        sleep(.1)
        pin.toggle()
        sleep(0.1)
    return False
    
