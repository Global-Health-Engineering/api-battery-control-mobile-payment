from machine import Pin
from utime import sleep

with open("isrgrootx1.pem", "rb") as f:
    data = f.read()
print(len(data)) #1939

def blink_led(pin: Pin):
    print("LED starts flashing...")
    while True:
        try:
            pin.toggle()
            sleep(1) # sleep 1sec
        except KeyboardInterrupt:
            break
    pin.off()
    print("Finished.")


