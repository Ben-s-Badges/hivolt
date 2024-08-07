import plugin
from text import textDraw

class plugin_visual:
    _name = 'scroll'
    _drawinterval = 25

    # Buffer for rendered scrolltext
    _scrolltext = None
    _scrolltext_offset = 0

    _messages = [
        "Hello world!   ",
        "DEFCON 32. Stickers come to the LVCC, at last   "
    ]

    def newMsg(self, message):
        # Allocate a buffer to hold rendered message & render into it
        self._scrolltext = self._textDraw.drawString(message)
        print('message',message, self._scrolltext)
        # Display from the start
        self._scrolltext_offset = 0

#    @micropython.native
    def scrollUpdate(self):
        text_offset = self._scrolltext_offset
        offset = 0
        
        # Get buffer
        screensize = len(self._screen)
        
        while True:
            # Remaining space
            space = screensize - offset
            if space == 0:
                break

            # Copy remaining text into start of screen buffer
            remaining = len(self._scrolltext) - text_offset
            tocopy = space if remaining > space else remaining
            self._screen[offset:] = self._scrolltext[text_offset:(text_offset + tocopy)]
            offset += tocopy
            
            # Start at the beginning of the scrolltext if we've copied it all
            text_offset = 0

        self._scrolltext_offset = (self._scrolltext_offset + 1) % len(self._scrolltext)
        
    def draw(self):
        self.scrollUpdate()
        return True

    def __init__(self, screen):
        self._screen = screen
        self._message = 0
        self._textDraw = textDraw()

        self.newMsg(self._messages[self._message])

    def input(self, i):
        if i == plugin.JOYSTICK_LEFT:
            self._message = (self._message + 1) % len(self._messages)
            self._scroller.newMsg(self._messages[self._message])
        elif i == plugin.JOYSTICK_RIGHT:
            self._message = (self._message - 1) % len(self._messages)
            self._scroller.newMsg(self._messages[self._message])
