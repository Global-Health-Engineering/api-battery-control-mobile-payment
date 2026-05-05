### This is the code for the RP2350 
### Functions are at the beginning, main code at the end
### It conatins diffrent AT commands to communicate with the SIM7670g module via UART

from machine import UART,Pin
from utime import sleep
import time

SIM_PIN = "8665"  #define your SIM card PIN here #721694673 #7816 #8665
UARL = "https://nonrotational-tatum-readier.ngrok-free.dev"
PATH_GET = '/Incoming/Charging/Request'
PATH_POST = '/Charging/Finsihed'

#--- Define UART--------------------------------
PWR = Pin(4, Pin.IN)  #for power up
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1), timeout=1000, txbuf=2048) #define the tx, rx pins and baudrate for UART 0 of pico
time.sleep(1)

#--- Power up function -----------------------------------------------------------------------------
#This function can be used to power up the SIM7670g module via the PWR pin
def power_upSIM7670():
    print("Power on module")
    PWR.init(Pin.OUT)     
    PWR.value(0)          
    time.sleep(1)    
    PWR.init(Pin.IN)      
    time.sleep(2)
    print("Power up done...")

#---initation of SIM module -----------------------------------------------------------------------------
#This function initialices the SIM7670g module for HTTP communication
def initSIM7670():
    send_at("AT", 1000, "OK")
    PINResponse = send_at_wait_resp("AT+CPIN?", 2000)
    if PINResponse and ("SIM PIN" in PINResponse):
        send_at(f'AT+CPIN="{SIM_PIN}"', 10000, "READY") #Enter SIM PIN if SIM not ready

    SignalResponse = send_at("AT+CSQ", 4000, "OK") #Check functionality: 1 = RF fully functional, 0,4 = RF off/ flight mode
    TimeStart = time.time()
    while SignalResponse and ("99,99" in SignalResponse):
        if time.time() - TimeStart < 120:
            print("Waiting for Signal...")
            time.sleep(2)
            SignalResponse = send_at("AT+CSQ", 4000, "OK")
        else:
            return print("No Signal found, timeout")

    RegResponse = send_at("AT+CFUN=1", 10000, "OK") #Set full functionality
    if not RegResponse or ("OK" not in RegResponse):
        return print("No Network Resigstration found!")
    send_at("AT+CNMI=0,0,0,0,0", 4000, "OK") #Disable unsolicited result codes for SMS
    send_at("AT+CGACT=1,1", 15000, "OK")  # Activate PDP context 1 / connect to mobile data
    print("IP of module: ", send_at_wait_resp("AT+CGPADDR=1", 5000))

#--- AT command function -----------------------------------------------------------------------------
#This function sends AT commands to the SIM7670g module and reads the response until expactet response appears
def send_at(cmd, timeout, expact):
    print('>>', cmd)
    uart.write((cmd + "\r\n").encode()) #has to end with carrage return (CR = \r), \n is optional
    t_start = time.ticks_ms()
    resp = ""                                # define an empty response
    while time.ticks_diff(time.ticks_ms(), t_start) < timeout: #processing until timeout
        if uart.any():
            chunk = uart.read().decode()
            resp += chunk 
            time.sleep_ms(2)            # short hold for all messages to arrive
            if expact in resp: #checking if the expactet response is equal to the response from module, than break
                print('<<', resp)
                sleep(.2)
                return resp
        else:
            time.sleep_ms(3)         # break for cpu
    print("<< Timeout...")
    print('<< Response so far is:', resp)
    sleep(1)
    return resp

#----- AT command function for collecting raw response --------------------------------------------------------
#This function sends AT command and reads all responses until time run out
def send_at_wait_resp(cmd, timeout):
    print('>>', cmd)
    uart.write((cmd + "\r\n").encode())
    t_start = time.ticks_ms()
    resp = ""
    while time.ticks_diff(time.ticks_ms(), t_start) < timeout:
        if uart.any():
            chunk = uart.read().decode()
            resp += chunk
            time.sleep_ms(50)            # short hold for all messages to arrive

        else:
            time.sleep_ms(10)         # break for cpu 
    print('<<', resp)
    return resp

#--- Certificate uploader -----------------------------------------------------------------------------
#This function allows to load certificates to SIM7670g module
def upload_certificateSIM7670():
    print("---------------------------SIM CERTIFICATE UPLOADER---------------------------")
    CertName = input("Please input the certificate filename (e.g. isrg_root.pem): ").strip()
    try:
        with open(CertName, "rb") as f: # getting length of certificate
            cert = f.read()
            length = len(cert)
            print("Certificate size:", length, "bytes")
    except OSError:
        print("Certificate file not found")
        return False

    uart.write(f'AT+CCERTDOWN="{CertName}",{length}\r\n'.encode()) #downloading certificate

    t0 = time.ticks_ms()
    prompt_received = False
    buffer = b""
    
    while time.ticks_diff(time.ticks_ms(), t0) < 5000: # checking prompt
        if uart.any():
            chunk = uart.read()
            buffer += chunk
            if b">" in buffer:
                prompt_received = True
                break
        time.sleep_ms(10)

    if not prompt_received:
        print("No '>' prompt received")
        return False
    
    uart.write(cert)    # Send certificate data
    time.sleep(1)
    if uart.any():  # Check for validation
        print(uart.read().decode())

#--- AT command function tester -----------------------------------------------------------------------------
#This function allows to manually input AT commands and see the response from the SIM7670g module
def test_atSIM7670(timeout=0):
    print("---------------------------SIM AT COMMAND TESTER---------------------------")
    print('Please input the AT command,press Ctrl+C to exit:')
    while True:
        try:
            cmd = input("> ").strip()
            if not cmd:
                continue
            t = 3000
            if "cfun" in cmd.lower():
                t = 15000 
            send_at_wait_resp(cmd, t)

        except KeyboardInterrupt:
            print('\n------Exit AT Command Test!------\r\n')
            break

#--- https get function tester -----------------------------------------------------------------------------
#This function allows to manually input a URL and perform an HTTPS GET request using the SIM7670 module

def test_httpGETSIM7670():
    print("---------------------------SIM HTTP GET TESTER---------------------------")
    print('Please input the command,press Ctrl+C to exit:')
    try:

        while True:
            TestURL = input("> Please input the URL: ").strip()
            CertName = input("> Please input the certification name: ").strip()
            send_at('AT+CSSLCFG="sslversion",0,3', 5000, "OK")
            send_at('AT+CSSLCFG="authmode",0,1', 5000, "OK")
            send_at('AT+CSSLCFG="ignorelocaltime",0,1', 5000, "OK")
            send_at(f'AT+CSSLCFG="cacert",0,"{CertName}"' , 5000, "OK")
            send_at('AT+CSSLCFG="enableSNI",0,1', 5000, "OK")

            send_at_wait_resp("AT+HTTPTERM", 2000) #close http 
            send_at("AT+HTTPINIT", 5000, "OK") #open http
            send_at('AT+HTTPPARA="SSLCFG",0', 5000, "OK") # enable SSL/TLS with configuration profile 0
            send_at(f'AT+HTTPPARA="URL","{TestURL}"', 8000, "OK") # set URL
            action_resp = send_at_wait_resp("AT+HTTPACTION=0", 10000)
            #example response:
            #OK
            #
            #+HTTPACTION: 0,200,104220  #--> 0 = GET, 200 = HTTP status "OK", 104220 = body length
            if (not action_resp) or ("200" not in action_resp): #if status code isn't "OK", terminate
                send_at_wait_resp("AT+HTTPTERM", 2000)
            else:
                send_at_wait_resp("AT+HTTPREAD?", 5000)
                send_at_wait_resp(f'AT+HTTPREAD=0,1500', 15000)

    except KeyboardInterrupt:
        print('\n------Exit https Test!------\r\n')
            

#--- https post function tester -----------------------------------------------------------------------------
#This function allows to manually input a URL and perform an HTTPS POST request using the SIM767
def test_httpPOSTSIM7670():
    print("---------------------------SIM HTTP POST TESTER---------------------------")
    print('Please input the command,press Ctrl+C to exit:')
    try:
        while True:
            TestURL = input("> Please input the URL: ").strip()
            CertName = input("> Please input the certification name: ").strip()
            send_at('AT+CSSLCFG="sslversion",0,3', 5000, "OK")
            send_at('AT+CSSLCFG="authmode",0,0', 5000, "OK")
            send_at('AT+CSSLCFG="ignorelocaltime",0,1', 5000, "OK")
            send_at(f'AT+CSSLCFG="cacert",0,"{CertName}"' , 5000, "OK")
            send_at('AT+CSSLCFG="enableSNI",0,1', 5000, "OK")

            send_at_wait_resp("AT+HTTPTERM", 2000) #close http 
            send_at("AT+HTTPINIT", 5000, "OK") #open http
        
            send_at('AT+HTTPPARA="SSLCFG",0', 5000, "OK") # enable SSL/TLS with configuration profile 0
            send_at(f'AT+HTTPPARA="URL","{TestURL}"', 8000, "OK") # set URL
            send_at('AT+HTTPPARA="CONTENT","application/json"', 5000, "OK")
            post_data = '{"temperature":1}'
            length = len(post_data)
            send_at(f"AT+HTTPDATA={length},1000", 5000, "DOWNLOAD")
            uart.write(post_data.encode())
            time.sleep(3)
            action_resp = send_at_wait_resp("AT+HTTPACTION=1", 10000)
            #example response:
            #OK
            #
            #+HTTPACTION: 1,200,104220  #--> 1 = POST, 200 = HTTP status "OK", 104220 = body length
            if (not action_resp) or ("200" not in action_resp): #if status code isn't "OK", terminate
                send_at_wait_resp("AT+HTTPTERM", 2000)
            else:
                send_at_wait_resp("AT+HTTPREAD?", 5000)
                send_at_wait_resp(f'AT+HTTPREAD=0,1500', 15000)

    except KeyboardInterrupt:
        print('\n------Exit https Test!------\r\n')
        

#--- Debug function -----------------------------------------------------------------------------
#Various AT commands give information about the status of the SIM7670 module
def debugSIM7670(): 
    print("----------------------SIM7670 DEBUG INFO-------------------------")
    print("The AT command tester will start automatically. Skip for automated testflow.")
    test_atSIM7670()
    test_httpPOSTSIM7670()
    test_httpGETSIM7670()
    send_at("AT", 2000,"OK") #Checking for UART connection to work
    ResponseSIM = send_at("AT+CPIN?", 4000, "READY")
    if ResponseSIM and ("SIM PIN" in ResponseSIM):
        send_at(f'AT+CPIN="{SIM_PIN}"', 10000, "READY") #Enter SIM PIN if SIM not ready
        send_at("AT+CPIN?", 4000, "READY")
    send_at("ATI", 4000, "OK") #Get moudule information
    send_at("AT+CFUN?", 4000, "OK") #Check functionality: 1 = RF fully functional, 0,4 = RF off/ flight mode
    send_at("AT+CSQ", 4000, "OK") # Check RF signal: 20-30 is good
    send_at("AT+CREG?", 5000, "OK") # Network registration on CS-Domain/2G,3G/GSM/Phone/SMS: 0 = not registered,1=registered home network, 2 = searching, 3 = denied,5=registered roaming
    send_at("AT+CGREG?",5000, "OK") # Network registration on PS-Domain/2G,3G/Internet: 0 = not registered,1=registered home network, 2 = searching, 3 = denied,5=registered roaming
    send_at("AT+CEREG?",5000, "OK") # Network registration on LTE-Domain/4G/LTE/Internet: 0 = not registered,1=registered home network, 2 = searching, 3 = denied,5=registered roaming
    send_at("AT+CPSI?", 5000, "OK") # LTE Service status: LTE,Online,
    send_at("AT+CGATT=1",4000, "OK") # Activate Packed Service (PS)/ activate mobile data
    APN_FALLBACK = ""   # z.B. "safaricom" oder dein IoT-APN; leer lassen wenn unbekannt
    send_at("AT+CGDCONT=?", 8000, "OK")# show what PDP types are supported (debug only)
    apn = APN_FALLBACK.strip() or None
    print(f"Using APN: {apn}")
    if apn:
        send_at(f'AT+CGDCONT=1,"IP","{apn}"', 8000, "OK")# Many modules accept APN with or without quotes; quotes are safest
    else:
        pass # If APN unknown, leave CGDCONT as-is and let the network/SIM defaults work 
    send_at("AT+CGACT=1,1", 15000, "OK")  # Activate PDP context 1 / connect to mobile data
    send_at("AT+CGACT?", 5000, "OK")    # verify activation PDP/ verify mobile data connected
    resp = send_at_wait_resp("AT+CGPADDR=1", 5000)    # get an IP address 
    print("IP of module: ", resp)
    test_atSIM7670()
    test_httpGETSIM7670()
    test_httpPOSTSIM7670()
    print("----------------------EXIT SIM7670 DEBUG-------------------------")    

##--- https get function -----------------------------------------------------------------------------
#This function performs an HTTPS GET request to the specified URL using the SIM7670g module   
def httpPOSTSIM7670(url,charger_number):

    send_at('AT+CSSLCFG="sslversion",0,3', 5000, "OK")
    send_at('AT+CSSLCFG="authmode",0,1', 5000, "OK")
    send_at('AT+CSSLCFG="ignorelocaltime",0,1', 5000, "OK")
    send_at('AT+CSSLCFG="enableSNI",0,1', 5000, "OK")

    send_at_wait_resp("AT+HTTPTERM", 2000) #close http 
    send_at("AT+HTTPINIT", 5000, "OK") #open http
    send_at(f'AT+HTTPPARA="URL","{url}"', 8000, "OK") # set URL
    send_at('AT+HTTPPARA="SSLCFG",0', 5000, "OK") # enable SSL/TLS with configuration profile 0
    send_at('AT+HTTPPARA="CONTENT","application/json"', 5000, "OK")
    post_data = f'{{"charger_number":"{charger_number}"}}'
    length = len(post_data)
    send_at(f"AT+HTTPDATA={length},1000", 5000, "DOWNLOAD")
    uart.write(post_data.encode())
    time.sleep(1)

    action_resp = send_at_wait_resp("AT+HTTPACTION=1", 25000)
    #example response:
    #OK
    #
    #+HTTPACTION: 0,200,104220  #--> 0 = GET, 200 = HTTP status "OK", 104220 = body length

    if (not action_resp) or ("200" not in action_resp): #if status code isn't "OK", terminate
        send_at_wait_resp("AT+HTTPTERM", 2000)
        return ""

    body_len = None # extract body length from response 
    for line in action_resp.splitlines():
        if "+HTTPACTION" in line:
            try:
                parts = line.split(":")[1].strip().split(",")
                body_len = int(parts[2])
            except:
                pass

    if body_len is None: #if body length couldn't be parsed, terminate
        send_at_wait_resp("AT+HTTPTERM", 2000)
        return ""

    data = send_at_wait_resp(f"AT+HTTPREAD=0,{body_len}", 15000)
    send_at_wait_resp("AT+HTTPTERM", 2000) 
    return extract_body_from_httpread(data)


##--- https get function -----------------------------------------------------------------------------
#This function performs an HTTPS GET request to the specified URL using the SIM7670g module   
def httpsPOSTSIM7670(url,cert):

    send_at('AT+CSSLCFG="sslversion",0,3', 5000, "OK")
    send_at('AT+CSSLCFG="authmode",0,1', 5000, "OK")
    send_at('AT+CSSLCFG="ignorelocaltime",0,1', 5000, "OK")
    send_at(f'AT+CSSLCFG="cacert",0,"{cert}"' , 5000, "OK")
    send_at('AT+CSSLCFG="enableSNI",0,1', 5000, "OK")

    send_at_wait_resp("AT+HTTPTERM", 2000) #close http 
    send_at("AT+HTTPINIT", 5000, "OK") #open http
    send_at(f'AT+HTTPPARA="URL","{url}"', 8000, "OK") # set URL
    send_at('AT+HTTPPARA="SSLCFG",0', 5000, "OK") # enable SSL/TLS with configuration profile 0
    send_at('AT+HTTPPARA="CONTENT","application/json"', 5000, "OK")
    post_data = '{"temperature":1}'
    length = len(post_data)
    send_at(f"AT+HTTPDATA={length},1000", 5000, "DOWNLOAD")
    uart.write(post_data.encode())
    time.sleep(1)

    action_resp = send_at_wait_resp("AT+HTTPACTION=1", 25000)
    #example response:
    #OK
    #
    #+HTTPACTION: 0,200,104220  #--> 0 = GET, 200 = HTTP status "OK", 104220 = body length

    if (not action_resp) or ("200" not in action_resp): #if status code isn't "OK", terminate
        send_at_wait_resp("AT+HTTPTERM", 2000)
        return ""

    body_len = None # extract body length from response 
    for line in action_resp.splitlines():
        if "+HTTPACTION" in line:
            try:
                parts = line.split(":")[1].strip().split(",")
                body_len = int(parts[2])
            except:
                pass

    if body_len is None: #if body length couldn't be parsed, terminate
        send_at_wait_resp("AT+HTTPTERM", 2000)
        return ""

    data = send_at_wait_resp(f"AT+HTTPREAD=0,{body_len}", 15000)
    send_at_wait_resp("AT+HTTPTERM", 2000) 
    return extract_body_from_httpread(data)

def httpGetSIM7670(url):
    send_at_wait_resp("AT+HTTPTERM", 1000) #close http 
    send_at("AT+HTTPINIT", 5000, "OK") #open http
    send_at(f'AT+HTTPPARA="URL","{url}"', 8000, "OK") # set URL
    send_at('AT+HTTPPARA="SSLCFG",0', 5000, "OK") # enable SSL/TLS with configuration profile 0
    action_resp = send_at_wait_resp("AT+HTTPACTION=0", 3000)
    #example response:
    #OK
    #
    #+HTTPACTION: 0,200,104220  #--> 0 = GET, 200 = HTTP status "OK", 104220 = body length

    if (not action_resp) or ("200" not in action_resp): #if status code isn't "OK", terminate
        print("HTTP GET failed or returned non-OK status")

    body_len = None # extract body length from response 
    for line in action_resp.splitlines():
        if "+HTTPACTION" in line:
            try:
                parts = line.split(":")[1].strip().split(",")
                body_len = int(parts[2])
            except:
                pass

    if body_len is None: #if body length couldn't be parsed, terminate
        send_at_wait_resp("AT+HTTPTERM", 2000)
        return ""

    data = send_at_wait_resp(f"AT+HTTPREAD=0,{body_len}", 3000)
    send_at_wait_resp("AT+HTTPTERM", 1000) 
    return extract_body_from_httpread(data)
##--- https get function -----------------------------------------------------------------------------
#This function performs an HTTPS GET request to the specified URL using the SIM7670g module   
def httpsGetSIM7670(url,cert):

    send_at('AT+CSSLCFG="sslversion",0,3', 5000, "OK")
    send_at('AT+CSSLCFG="authmode",0,1', 5000, "OK")
    send_at('AT+CSSLCFG="ignorelocaltime",0,1', 5000, "OK")
    send_at(f'AT+CSSLCFG="cacert",0,"{cert}"' , 5000, "OK")
    send_at('AT+CSSLCFG="enableSNI",0,1', 5000, "OK")

    send_at_wait_resp("AT+HTTPTERM", 2000) #close http 
    send_at("AT+HTTPINIT", 5000, "OK") #open http
    send_at(f'AT+HTTPPARA="URL","{url}"', 8000, "OK") # set URL
    send_at('AT+HTTPPARA="SSLCFG",0', 5000, "OK") # enable SSL/TLS with configuration profile 0
    action_resp = send_at_wait_resp("AT+HTTPACTION=0", 25000)
    #example response:
    #OK
    #
    #+HTTPACTION: 0,200,104220  #--> 0 = GET, 200 = HTTP status "OK", 104220 = body length

    if (not action_resp) or ("200" not in action_resp): #if status code isn't "OK", terminate
        send_at_wait_resp("AT+HTTPTERM", 2000)
        return ""

    body_len = None # extract body length from response 
    for line in action_resp.splitlines():
        if "+HTTPACTION" in line:
            try:
                parts = line.split(":")[1].strip().split(",")
                body_len = int(parts[2])
            except:
                pass

    if body_len is None: #if body length couldn't be parsed, terminate
        send_at_wait_resp("AT+HTTPTERM", 2000)
        return ""

    data = send_at_wait_resp(f"AT+HTTPREAD=0,{body_len}", 15000)
    send_at_wait_resp("AT+HTTPTERM", 2000) 
    return extract_body_from_httpread(data)

##--- body extract function -----------------------------------------------------------------------------
#This function extracts the body from the HTTPREAD response
def extract_body_from_httpread(resp: str):
    if not resp:
        return ""

    # Robust: extract the JSON/object payload between first "{" and last "}"
    start = resp.find("{")
    end = resp.rfind("}")
    if start != -1 and end != -1 and end > start:
        return resp[start:end+1].strip()

    # Fallback: old behavior (best effort)
    i = resp.find("\n")
    if i == -1:
        return resp.strip()
    body = resp[i+1:]
    body = body.replace("\r", "")
    body = body.replace("\nOK\n", "\n").strip()
    return body.strip()

