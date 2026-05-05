###---------------------------------------------------------------------------------------
### This micropython script is designed to run on a Raspberry Pi Pico in the charger
### There are functions for http, https GET and POST requests via SIM7670g module
###  and certificate upload funciton in the comments.
### During the development process it was decided to use http and not https
###  to reduce certifacte issues
###--------------------------------------------------------------------------------------
   

import json
from machine import Pin, UART
from utime import sleep
import time
#from blink import blink_led
from uart1pico1 import Uart1Pico1Open, Uart1Pico1Close, Uart1Pico1Response
from CurrentSensor import Currentmeasure
from CurrentSensor import measure_offset
from SIM7670g import power_upSIM7670, initSIM7670, httpGetSIM7670,httpsGetSIM7670, httpPOSTSIM7670, httpsPOSTSIM7670
from SIM7670g import test_atSIM7670, test_httpGETSIM7670,test_httpPOSTSIM7670, debugSIM7670
from SIM7670g import upload_certificateSIM7670
from SIM7080g import power_upSIM7080, initSIM7080, httpsGetSIM7080
from SIM7080g import test_atSIM7080, test_httpSIM7080, debugSIM7080

ButtonLED = Pin(19, Pin.OUT, value=0)
button = Pin(18, Pin.IN, Pin.PULL_UP)

dt = 0.5          # Messintervall [s] (muss zu Currentmeasure passen!)
voltage = 54.0    # System Voltage  

charger_number = 1111 #charger number must be a unique 4 digit intiger number
TIER_TO_WH_LIMIT = {
    20: 140, # Tier 20: 140 Wh (20% of 700 Wh)
    40: 280.0, # Tier 40: 280 Wh (40% of 700 Wh)
    80: 560.0
}

#---------start-------------------------------------------------------------------------------

ButtonLED.toggle()
sleep(.1)
ButtonLED.toggle()
sleep(.1)
ButtonLED.toggle()
sleep(.1)
ButtonLED.toggle()

print("Waiting for button...") #waiting for pressed button to start charging flow
while button.value() == 1:
    sleep(0.2)
print("Button pressed")

try:
    ButtonLED.value(1) 
    power_upSIM7670() #power up sim module
    ButtonLED.value(0)
    sleep(1)
    
    sleep(4)
    ButtonLED.value(1)
    sleep(2)
    ButtonLED.value(0)
    initSIM7670() #initialice sim module for http communication
    #upload_certificateSIM7670()

except Exception as e:
    print(f"Error during SIM7670 initialization: {e}")

start = time.time()
while time.time() - start < 180:
    
    sleep(2)
    ButtonLED.value(1)
    sleep(2)
    ButtonLED.value(0)

    uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5), timeout=1000) #define the tx, rx pins and baudrate for UART 0 of pico

    try:
        #debugSIM7670() #for debugging, include AT command tester
        #data = json.loads(httpsGetSIM7670("https://nonrotational-tatum-readier.ngrok-free.dev/Incoming/Charging/Request","isrgrootx1.pem")) 
        #other Testhosts "http://httpbin.org/get"; "https://httpbin.org/get", "Amazon Root CA 1.der; "https://eu.thingsboard.cloud/api/v1/3i0zuud6htbt79qlylig/telemetry","isrgrootx1.pem""
        data = json.loads(httpPOSTSIM7670("http://charge-ewaka.com/Incoming/Charging/Request",charger_number))
        print("Received data:", data)
        granted = (str(data.get("ChargingStatus", "")).lower() == "granted")
        tier = int(data.get("Tier", 0))
        sleep(2)


        if granted: #if charging granted initialice current sensor
            Wh_sum = 0.0
            offset = measure_offset()
            print("ACS712 offset ADC counts:", offset)
            sleep(.5)
            
            ButtonLED.value(1)  #turn on LED steady to indicate charging started
            Uart1Pico1Open(uart)
            
            confirmation_received = False
            StartWaiting = time.time()
            while time.time() - StartWaiting < 60:
                if Uart1Pico1Response(uart): #check if gate is open via uart communication with pico in gate
                    print("Gate is open. Confirmation received.")
                    confirmation_received = True
                    break
                else:
                    sleep(2)
                    Uart1Pico1Open(uart)
                    print("No confirmation received. Retrying...")          

            if not confirmation_received:
                print("No UART confirmation within timeout. Aborting charging.")
                raise RuntimeError("UART confirmation timeout")
            
            if tier == 20:
                wh_limit = TIER_TO_WH_LIMIT[20]
            elif tier == 40:
                wh_limit = TIER_TO_WH_LIMIT[40]
            elif tier == 80:
                wh_limit = TIER_TO_WH_LIMIT[80]
            else:
                wh_limit = 140.0    # default to tier 20

            while Wh_sum < wh_limit: #charge until tier/ wh_limit achieved
                I = Currentmeasure(offset,dt)
                Wh_sum += voltage * I * dt / 3600
            print("Charging session ended.")
            print("Charged amount:", Wh_sum)

            ButtonLED.value(0)  #turn off LED

    except Exception as e:
        print(f"Error in main charging loop: {e}")
    
    finally:
        sleep(1)
        Uart1Pico1Close(uart) 
        sleep(1)