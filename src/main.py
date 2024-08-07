# 20240806 hfiennes@gmail.com
# I'm not very good at python. Can you tell? :)

from machine import Pin
import time, random, sys, os

from power import powerDriver
from screen import screenDriver
from joystick import joystickDriver
from accelerometer import accelerometerDriver

from bolt import boltAnimator
from text import textDraw

import plugin
import uctypes

# Sitting here until I write the microphone driver
MIC_SUPPLY = Pin(11, mode=Pin.OUT, value=0)

# Get peripherals
screen = screenDriver()
power = powerDriver()

# Queue for events to be delivered to plugins
eventq = []

# Input drivers
joystick = joystickDriver(eventq)
accelerometer = accelerometerDriver(eventq)

# Screen buffers in sensible format (not the native hardware format)
boltBuffer = bytearray(8)
screenBuffer = bytearray(240)

# Font plotter
text = textDraw()

# Visuals are implemented by plugins; any .py file in the plugin directory is added to the carousel
# Reorder them by altering their filenames
plugins = []
for p in os.listdir('/plugins'):
    if (p.endswith('.py')):
        module = p[:-3]
        plugins.append( { 'name': module, 'plugin': __import__('/plugins/'+module) })

# Initialize plugins by passing them the screen buffer
for p in plugins:
    print('initializing plugin', p['name'])
    p['instance'] = p['plugin'].plugin_visual(screenBuffer)

# Get a bolt animator
bolt = boltAnimator(boltBuffer)

# Push buffer to screen (to blank it) & start refresh cycles
screen.flushBolt(boltBuffer)
screen.flushScreen(screenBuffer)
screen.startRefresh()

# We wrap the following bits in a try in order to 
try:
    # Render welcome message
    text.drawString('   Ben\'s Badges', screenBuffer, 150, True)
    text.drawString('   Ben\'s Badges', screenBuffer, 235, True)
    text.drawString('vbat %.2fv' % (power.batteryVoltage()), screenBuffer, 14)
    screen.flushScreen(screenBuffer)

    # Animate bolt
    for i in range(0, bolt.length()):
        bolt.updateBolt()
        screen.flushBolt(boltBuffer)
        screen.flushScreen(screenBuffer)
        time.sleep(0.05)

    # Start at plugin 0
    plugin_selected = 0
    active_plugin = plugins[plugin_selected]['instance']
    
    # Intervals for bolt & accelerometer poll
    BOLTTICK = const(40)
    ACCELTICK = const(25)

    # Timers
    now = time.ticks_ms()
    refresh_plugin = now
    refresh_bolt = now
    poll_accelerometer = now
    second = now
    
    # Main loop
    while True:
        now = time.ticks_ms()
        
        # Update bolt if needed
        if now > refresh_bolt:
            # Update, note that you need to flush the screen after flushing the bolt
            bolt.updateBolt()
            screen.flushBolt(boltBuffer)
            screen.flushScreen(screenBuffer)
            
            refresh_bolt += BOLTTICK

        if now > refresh_plugin:
            # Call the plugin
            if active_plugin.draw():
                screen.flushScreen(screenBuffer)
                           
            # Reschedule (plugin can change drawinterval at any time)
            refresh_plugin = now + active_plugin._drawinterval

        # UUDDLRLR
        # Check for input
        if len(eventq) > 0:
            event = eventq.pop(0)
            
            # Catch push joystick
            if event[0] == plugin.EVENT_JOYSTICK and event[1] == plugin.JOYSTICK_PUSH:
                # Switch plugin
                plugin_selected = (plugin_selected + 1) % len(plugins)
                active_plugin = plugins[plugin_selected]['instance']
                print('switching to plugin', active_plugin._name)
            else:
                # Send all events to plugins
                active_plugin.input(event)

        if now > poll_accelerometer:
            poll_accelerometer = now + ACCELTICK
            eventq.append((plugin.EVENT_ACCEL, accelerometer.xyz()))
            
        if now > second:
            second = now + 1000
            #print(screen.refreshes(), fps)

# Clean up DMA, PIO etc on exit
except KeyboardInterrupt:
    # Separate because it doesn't seem to be caught by the generic one below
    screen.stopRefresh()
    print('exiting')
    
except Exception as e:
    # If we're stopping, stop the screen refresh neatly
    screen.stopRefresh()    
    raise e

