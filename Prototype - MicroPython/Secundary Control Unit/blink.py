from utime import sleep

def blink_led(pin):
    print("LED starts flashing...")
    while True:
        try:
            pin.toggle()
            sleep(1) # sleep 1sec
        except KeyboardInterrupt:
            break
    pin.off()
    print("Finished.")
