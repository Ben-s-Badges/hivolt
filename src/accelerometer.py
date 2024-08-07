from machine import Pin, I2C
import time, ustruct
import plugin

class accelerometerDriver:
    def irq(self, pin):
        print('irq')

    def xyz(self):
        data = self._i2c.readfrom_mem(0x18, 0xa8, 6)
        x = ustruct.unpack('<h', data[0:2])[0] / 16384
        y = ustruct.unpack('<h', data[2:4])[0] / 16384
        z = ustruct.unpack('<h', data[4:6])[0] / 16384
        return(x, y, z)
    
    def __init__(self, queue):
        self._queue = queue
        self._i2c = I2C(0,sda=Pin(12), scl=Pin(13), freq=100_000)
        
        # Check chip is there
        whoami = self._i2c.readfrom_mem(0x18, 0x0f, 1)[0]
        if whoami != 0x33:
            print('Invalid accelerometer ID')

        # Set 50Hz ODR, all axes
        self._i2c.writeto_mem(0x18, 0x20, b'\x47')
        
        if False:            
            # Enable IRQs... this isn't working for me
            self._i2c.writeto_mem(0x18, 0x22, b'\x10')
            self._i2c.writeto_mem(0x18, 0x25, b'\x02')
            
            # Interrupt
            ACCEL_INT = Pin(14, mode=Pin.IN, pull=Pin.PULL_UP)
            ACCEL_INT.irq(handler=self.irq, trigger=Pin.IRQ_FALLING)

