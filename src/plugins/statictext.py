import plugin
from text import textDraw

# Draw static messages on all 3 sides, with a background fill style changed by up
# Left and right change the message
# Down makes it flash

class plugin_visual:
    _name = 'statictext'
    _drawinterval = 500

    # Note \x80 is a single column blank
    _messages = [
        "\x80Keep LEFT",
        "\x80Keep RIGHT",
        "\x80WTF",
        "\x80DANGER",
        "\x80ANGER",
        "\x80Beer required",
    ]
    
    _backgrounds = [ 0x00, 0x18, 0x24, 0x42, 0x81, 0xc3, 0xe7 ]

    def draw(self):
        # Clear the screen
        for i in range(0, plugin.SCREEN_SIZE):
            self._screen[i] = self._backgrounds[self._background]
         
        self._state = 1 - self._state

        # Measure the string so we can center it. 72 pixels as that's the non-curved part
        width = self._textDraw.measureString(self._messages[self._message])
        offset = (72 - width) // 2
        
        if self._flashing and self._state:
            # Blank out areas where we would have had text
            for i in range(offset, offset+width):
                self._screen[i] = 0
            for i in range(232-offset, 232-offset-width, -1):
                self._screen[i] = 0
            for i in range(152-offset, 152-offset-width, -1):
                self._screen[i] = 0
        else:
            # Draw it reversed on left and right, and not reversed on the bottom
            self._textDraw.drawString(self._messages[self._message], self._screen, offset)
            self._textDraw.drawString(self._messages[self._message], self._screen, 232 - offset, True)
            self._textDraw.drawString(self._messages[self._message], self._screen, 152 - offset, True)
        return True

    def __init__(self, screen):
        self._screen = screen
        self._message = 0
        self._background = 0
        self._state = 0
        self._flashing = False
        self._textDraw = textDraw()

    def input(self, i):
        if i[0] != plugin.EVENT_JOYSTICK:
            return
        if i[1] == plugin.JOYSTICK_LEFT:
            self._message = (self._message + 1) % len(self._messages)
        elif i[1] == plugin.JOYSTICK_RIGHT:
            self._message = (self._message - 1) % len(self._messages)
        elif i[1] == plugin.JOYSTICK_UP:
            self._background = (self._background - 1) % len(self._backgrounds)
        elif i[1] == plugin.JOYSTICK_DOWN:
            self._flashing = not self._flashing
        self.draw()

