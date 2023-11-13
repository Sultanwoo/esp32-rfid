from time import sleep
import _thread

grn = None
red = None
prev_raw_uid = None
prev_card_id = None
    
class LED_GLOBAL_VAR:
    blink = False 
    g_blink = False
    off = False
    write_blink = False
    write_g_blink = False
    write_off = False
    
class INTERNAL: #write functions are just reverse
    def turning_off():
        global grn
        global red
        global prev_raw_uid
        global prev_card_id
        sleep(3)
        grn.value(0)
        red.value(0)
        prev_raw_uid = None
        prev_card_id = None
        LED_GLOBAL_VAR.off = False

    def blinking():
        global grn
        global red
        while 1:
            if not LED_GLOBAL_VAR.blink:
                break
            red.value(0)
            grn.value(1)
            sleep(0.1)
            if not LED_GLOBAL_VAR.blink:
                break
            grn.value(0)
            red.value(1)
            sleep(0.1)
        red.value(0)
        grn.value(0)
        
    def g_blinking():
        global grn
        while 1:
            if not LED_GLOBAL_VAR.g_blink:
                break
            grn.value(1)
            sleep(0.1)
            if not LED_GLOBAL_VAR.g_blink:
                break
            grn.value(0)
            sleep(0.1)
        grn.value(0)
        
        
    def write_turning_off():
        global grn
        global red
        global prev_raw_uid
        global prev_card_id
        sleep(3)
        grn.value(1)
        red.value(1)
        prev_raw_uid = None
        prev_card_id = None
        LED_GLOBAL_VAR.write_off = False

    def write_blinking():
        global grn
        global red
        while 1:
            if not LED_GLOBAL_VAR.write_blink:
                break
            red.value(0)
            grn.value(0)
            sleep(0.1)
            if not LED_GLOBAL_VAR.write_blink:
                break
            grn.value(1)
            red.value(1)
            sleep(0.1)
        red.value(1)
        grn.value(1)
        
    def write_g_blinking():
        global grn
        while 1:
            if not LED_GLOBAL_VAR.write_g_blink:
                break
            grn.value(0)
            sleep(0.1)
            if not LED_GLOBAL_VAR.write_g_blink:
                break
            grn.value(1)
            sleep(0.1)
        grn.value(1)

def turn_off():
    global grn
    global red
    if LED_GLOBAL_VAR.off:
        return
    if grn.value() == 1 or red.value() == 1:
        LED_GLOBAL_VAR.off = True
        _thread.start_new_thread(INTERNAL.turning_off, ())
        #print("thread turning off")

def blink_on():
    if not LED_GLOBAL_VAR.blink:
        LED_GLOBAL_VAR.blink = True
        _thread.start_new_thread(INTERNAL.blinking, ())
        #print("thread blinking")

def g_blink_on():
    if not LED_GLOBAL_VAR.g_blink:
        LED_GLOBAL_VAR.g_blink = True
        _thread.start_new_thread(INTERNAL.g_blinking, ())
        #print("thread g_blinking")
        
def blink_off():
    LED_GLOBAL_VAR.blink = False
    sleep(0.1) #for blinking to finish

def g_blink_off():
    LED_GLOBAL_VAR.g_blink = False
    sleep(0.1)
    
    
def write_turn_off():
    global grn
    global red
    if LED_GLOBAL_VAR.write_off:
        return
    if grn.value() == 0 or red.value() == 0:
        LED_GLOBAL_VAR.write_off = True
        _thread.start_new_thread(INTERNAL.write_turning_off, ())
        #print("thread turning off")

def write_blink_on():
    if not LED_GLOBAL_VAR.write_blink:
        LED_GLOBAL_VAR.write_blink = True
        _thread.start_new_thread(INTERNAL.write_blinking, ())
        #print("thread blinking")

def write_g_blink_on():
    if not LED_GLOBAL_VAR.write_g_blink:
        LED_GLOBAL_VAR.write_g_blink = True
        _thread.start_new_thread(INTERNAL.write_g_blinking, ())
        #print("thread g_blinking")
        
def write_blink_off():
    LED_GLOBAL_VAR.write_blink = False
    sleep(0.1) #for blinking to finish

def write_g_blink_off():
    LED_GLOBAL_VAR.write_g_blink = False
    sleep(0.1)
