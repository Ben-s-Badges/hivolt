# hivolt
Software and hardware details for the Ben's Badges HiVolt badge 2024

# Quick start

Got your badge and want to personalize the messages? Here's the quick guide!

1. Install Thonny. This is a python IDE which includes support to talk to micropython running on an embedded device. You can download it here for win/mac/linux: https://thonny.org/
2. Configure it to use the RP2040 backend, in the settings menu:

![thonny setup dialog][docs/thonny-config.jpg]

...then click ok, plug the badge in, and turn it on.

3. Connect to the badge by pressing the 'stop' button in Thonny. The badge should go blank, and you should see a '>>>' REPL prompt in the Thonny window, and the tree in the left sidebar should show the files on the badge filesystem.
4. Pop open the "plugins" folder.

![thonny sidebar showing plugins][docs/thonny-plugins.jpg]

5. To change the scrolltext, open the '00-scroll.py' file. You can add as many lines as you want - it's a python array, so commas after each string. Press save, then with the badge still connected, double click the 'main.py' and press the play button to run the code and check your messages appear. Use left and right joystick clicks when in the scrolltext mode to switch messages. If it's all ok then you can disconnect the badge - you already saved the changes to the file onto the device so it's persistent.

![thonny showing scrolltext file][docs/thonny-scrolltext.jpg]

6. To change the static text, open the 'statictext.py' file - here, the strings have to be shorter to fit on the display. You can see I am using the '\x80' character to add a single blank column before the first character - characters have a blank column at the end, and the one at the start makes it look prettier. You may want to do the same.

![thonny showing statictext file][docs/thonny-statictext.jpg]

You can also noodle around with the other files to change what they do, or to look at what controls they have implemented. If you make your own plugin, you just need to drop it into the folder and it'll get picked up. The folder is scanned in alphabetical order and that defines the order they appear as you click through them - this is why the scrolltext name starts with 00, to make it first at boot.

# Hardware

See hardware.md, but also:

- There are two holes in the back of the badge. One is oval. This is above the microphone, do not stick things into this hole.
- The other hole is paperclip sized, and leads to the BOOT button for the RP2040. To enter RP2040 DFU mode, turn the badge off, hold the button with a paperclip, and then turn it on. The device should appear on USB as a drive, and you then drag and drop uf2 files to it to (eg) reload micropython, or load any other Pi code.

# Software

All the files inside src need to go to the badge; main.py is automatically run on boot, so that's the main badge startup code. These are all pre-loaded onto badges before delivery, but if you want to nuke it from orbit, use flash_nuke.uf2 to erase everything, then re-load micropython and the source files from the repo.

I suggest using mpremote to copy everything over:

```
cd src
mpremote fs cp --recursive . :
```

Visuals are provided by plugins, which sit within the plugins/ folder on the device. They're pretty simplistic, as you can see. They have a refresh interval which is used to determine how often
to ask them to redraw, an input handler (which accepts joystick & accelerometer events), and an __init__ call where they get passed the screen buffer so they know where to draw.

This is still a work in progress. And I'm not great at python. Send help.
