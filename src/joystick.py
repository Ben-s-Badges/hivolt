from machine import Pin
import time
import plugin

class joystickDriver:
    SW_UP = Pin(24, mode=Pin.IN, pull=Pin.PULL_UP)
    SW_PUSH = Pin(15, mode=Pin.IN, pull=Pin.PULL_UP)
    SW_RIGHT = Pin(23, mode=Pin.IN, pull=Pin.PULL_UP)
    SW_LEFT = Pin(22, mode=Pin.IN, pull=Pin.PULL_UP)
    SW_DOWN = Pin(25, mode=Pin.IN, pull=Pin.PULL_UP)
    
    def irq(self, pin):
        # Ignore events for 250ms after they have triggered
        now = time.ticks_ms()
        if now < self._debounce:
            return
        
        if pin == self.SW_UP:
            self._queue.append((plugin.EVENT_JOYSTICK, plugin.JOYSTICK_UP))
        elif pin == self.SW_DOWN:
            self._queue.append((plugin.EVENT_JOYSTICK, plugin.JOYSTICK_DOWN))
        elif pin == self.SW_LEFT:
            self._queue.append((plugin.EVENT_JOYSTICK, plugin.JOYSTICK_LEFT))
        elif pin == self.SW_RIGHT:
            self._queue.append((plugin.EVENT_JOYSTICK, plugin.JOYSTICK_RIGHT))
        elif pin == self.SW_PUSH:
            self._queue.append((plugin.EVENT_JOYSTICK, plugin.JOYSTICK_PUSH))

        self._debounce = now + 250
            
    def __init__(self, queue):
        # Buffer for events
        self._queue = queue
        
        # Debounce timer (ms)
        self._debounce = 0

        # Configure interrupts on falling edges
        self.SW_UP.irq(handler=self.irq, trigger=Pin.IRQ_FALLING)
        self.SW_DOWN.irq(handler=self.irq, trigger=Pin.IRQ_FALLING)
        self.SW_LEFT.irq(handler=self.irq, trigger=Pin.IRQ_FALLING)
        self.SW_RIGHT.irq(handler=self.irq, trigger=Pin.IRQ_FALLING)
        self.SW_PUSH.irq(handler=self.irq, trigger=Pin.IRQ_FALLING)
        