# hivolt
Software and hardware details for the Ben's Badges HiVolt badge 2024

# Hardware

See hardware.md

# Software

All the files inside src need to go to the badge; there's the main file (badge.py) which can be renamed to main.py for auto-boot.

I suggest using mpremote to copy everything over:

```
cd src
mpremote fs cp -R . :/
```

Visuals are provided by plugins, which sit within the plugins/ folder on the device. They're pretty simplistic, as you can see. They have a refresh interval which is used to determine how often
to ask them to redraw, an input handler (which accepts joystick & accelerometer events), and an __init__ call where they get passed the screen buffer so they know where to draw.

This is still a work in progress. And I'm not great at python. Send help.
