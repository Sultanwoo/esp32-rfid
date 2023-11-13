import ntptime
import time
import _thread
from mfrc522 import MFRC522
from machine import Pin, SPI

#Location hardcoded
factory_address = "Factory 1"

#button
button = Pin(2, Pin.IN)
button_pressed = False #False for default and True for writing mode
button_rising = False 
button_falling = False
write = False #for light switch w/o sleep
def handle_rising(pin):
    global button_rising
    global button_falling
    if button_rising:
        return
    button_rising = True
    button_falling = False
    button.irq(trigger=Pin.IRQ_FALLING, handler=handle_falling)
def handle_falling(pin):
    global button_falling
    global button_rising
    if button_falling:
        return
    button_falling = True
    button_rising = False
    global button_pressed
    button_pressed = not button_pressed
    #print("button pressed")
    button.irq(trigger=Pin.IRQ_RISING, handler=handle_rising)
button.irq(trigger=Pin.IRQ_RISING, handler=handle_rising)

#LED pins
import led as Led
Led.grn = Pin(21, Pin.OUT)
Led.red = Pin(22, Pin.OUT)
Led.grn.value(0)
Led.red.value(1)

#Wifi networks
networks_dict = {
    "NUdormitory": "1234512345",
    "Erasyl": "13072011",
    "NU": "1234512345"
}

#Connect to Wifi
import network
def do_connect():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active():
        wlan.active(True)
    if not wlan.isconnected():
        print("Scanning available networks")
        ssid = wlan.scan()
        for x in ssid:
            for wifi_ssid in networks_dict:
                if wifi_ssid in str(x):
                    print('Connecting to ' + str(wifi_ssid))
                    wlan.connect(wifi_ssid, networks_dict[wifi_ssid])
                    while not wlan.isconnected():
                        pass
                    break
            if wlan.isconnected():
                break
            
try:
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active() or not wlan.isconnected():
        do_connect()
    if not wlan.active() or not wlan.isconnected():
        print("Couldn't connect")
        exit()
    print('Connected!\nNetwork config:', wlan.ifconfig())
    
except Exception as e:
    print(str(e))
    
#set datetime
try:
    ntptime.settime() #too frequent queries will result in KoD, restart frequency > 15 sec 
except Exception as e:
    print(str(e))
#firebase 
import ufirebase as firebase
firebase.setURL("https://rfid-fb-67174-default-rtdb.asia-southeast1.firebasedatabase.app")
#firebase.setURL("https://rfid-aa9b8-default-rtdb.asia-southeast1.firebasedatabase.app") #RFID

#Read tag
spi = SPI(2, baudrate=2500000, polarity=0, phase=0)
spi.init()
#spi communication protocol
rdr = MFRC522(spi=spi, gpioRst=4, gpioCs=5)
print("Please, place the tag")
time.sleep(0.01)
Led.red.value(0)

while True:
    (stat, tag_type) = rdr.request(rdr.REQIDL)
    if button_pressed:
        #if first time after button pressed don't sleep
        if not write:
            write = True
            Led.grn.value(1)
            Led.red.value(1)
            Led.prev_raw_uid = None
            Led.prev_card_id = None
            
        Led.write_turn_off()
        if stat == rdr.OK:
            (stat, raw_uid) = rdr.anticoll()
            #to avoid sending multiple times
            if Led.prev_raw_uid == raw_uid:
                print("UID:", Led.prev_card_id, "is not checked")
                continue
            Led.write_blink_on()
            
            if stat == rdr.OK:
                card_id = "0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
                print("UID:", card_id, end=' ')
                tags_path = "Tags/" + card_id
                firebase.get(tags_path, "var1", bg=0)
                Led.write_blink_off()
                
                if firebase.var1 != None:
                    print("is in database")
                    Led.grn.value(0)
                else:
                    Led.write_g_blink_on()
                    factory_path = "Factories/" + factory_address
                    date = time.localtime(time.time() + (+6 * 3600))
                    date = date[:6]
                    tags_address = factory_address + ' ' + str(date[2]) + '-' + str(date[1]) + '-' + str(date[0])
                    tags_date = str(date[3]) + ':' + str(date[4]) + ':' + str(date[5])
                    factory_date = str(date[2]) + '-' + str(date[1]) + '-' + str(date[0]) + ' ' + str(date[3]) + ':' + str(date[4]) + ':' + str(date[5])
                    print(factory_date, end='')
                    #bg set to False to force finish sending, reason limited RAM
                    firebase.patch(tags_path, {tags_address: tags_date}, False, 0)
#turn on                    #firebase.patch(factory_path, {card_id: factory_date}, False, 1)
                    print(" written in database")
                    Led.write_g_blink_off()
                    Led.grn.value(1)
                Led.prev_raw_uid = raw_uid
                Led.prev_card_id = card_id
                
    else:
        if write:
            write = False
            Led.grn.value(0)
            Led.red.value(0)
            Led.prev_raw_uid = None
            Led.prev_card_id = None
        
        Led.turn_off()
        if stat == rdr.OK:
            (stat, raw_uid) = rdr.anticoll()
            #to avoid sending multiple times
            if Led.prev_raw_uid == raw_uid:
                print("UID:", Led.prev_card_id, "is not sent") #green
                continue
            Led.blink_on()
             
            if stat == rdr.OK:
                #print("type: 0x%02x" % tag_type)
                card_id = "0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
                print("UID:", card_id, end=' ')
                tags_path = "Tags/" + card_id
                #add uids to database with value other than None!
                firebase.get(tags_path, "var1", bg=0)
                Led.blink_off()
                
                if firebase.var1 != None: #green led blinking
                    Led.g_blink_on()
                    factory_path = "Factories/" + factory_address
                    date = time.localtime(time.time() + (+6 * 3600))
                    date = date[:6]
                    tags_address = factory_address + ' ' + str(date[2]) + '-' + str(date[1]) + '-' + str(date[0])
                    tags_date = str(date[3]) + ':' + str(date[4]) + ':' + str(date[5])
                    factory_date = str(date[2]) + '-' + str(date[1]) + '-' + str(date[0]) + ' ' + str(date[3]) + ':' + str(date[4]) + ':' + str(date[5])
                    print(factory_date, end='')
                    #bg set to False to force finish sending, reason limited RAM
                    firebase.patch(tags_path, {tags_address: tags_date}, False, 0)
#turn on                    firebase.patch(factory_path, {card_id: factory_date}, False, 1)
                    print(" sent")
                    Led.g_blink_off()
                    Led.grn.value(1)
                else:
                    print("is not in database") #red led 1 sec
                    Led.red.value(1)
                Led.prev_raw_uid = raw_uid
                Led.prev_card_id = card_id
                