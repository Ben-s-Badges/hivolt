# Class to deal with the battery, charger, and monitoring voltages
from machine import Pin, ADC
import time

class powerDriver():
    BATTVOLTEN = Pin(4, mode=Pin.OUT, value=0)
    BATTVOLT = ADC(Pin(26))
    BUSVOLT = ADC(Pin(27))
    nCHRG = Pin(10, mode=Pin.IN, pull=Pin.PULL_UP)

    def batteryVoltage(self):
        # Read battery
        self.BATTVOLTEN.on()
        time.sleep(0.001) # Delay for sample capacitor
        vbat = (self.BATTVOLT.read_u16() / 65535.0) * 3.3 / (100.0/133.0)
        self.BATTVOLTEN.off()
        return vbat
    
    def usbVoltage(self):
        # Read VBUS
        vbus = (self.BUSVOLT.read_u16() / 65535.0) * 3.3 / (150.0/250.0)
        return vbus
    
    def isCharging(self):
        return True if nCHRG.value() == 0 else False
