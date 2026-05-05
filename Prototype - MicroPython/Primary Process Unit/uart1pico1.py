from machine import Pin
from utime import sleep

pin = Pin("LED", Pin.OUT)

def Uart1Pico1Open(uart):
    
    pin.toggle()
    sleep(0.5)
    message = uart.write(b'Hello from Pico! Open gate\n')
    sleep(0.5)
    print (message)
    pin.toggle()

    sleep(1)


def Uart1Pico1Close(uart):
    pin.toggle()
    sleep(0.5)
    message = uart.write(b'Goodbye from Pico! Close gate\n')
    sleep(0.5)
    print (message)
    pin.toggle()

    sleep(1)

    pin.toggle()
    sleep(0.5)
    message = uart.write(b'Goodbye from Pico! Close gate\n')
    sleep(0.5)
    print (message)
    pin.toggle()

def Uart1Pico1Response(uart):
    try:
        if uart.any():
            pin.toggle()
            sleep(1)
            resp = uart.read().decode()
            sleep(0.5)
            pin.toggle()
            print(resp)
            if 'Hello from Pico! Gate is open' in resp:
                return True
            else:
                return False
        sleep(2)
        return False
    except Exception as e:
        return False
