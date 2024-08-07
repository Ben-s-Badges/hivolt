import plugin

class plugin_visual:
    _name = 'meter'
    _drawinterval = 5

    #@micropython.native
    def meterUpdate(self):
        self.left += self.dl
        if (self.left >= self.max): self.dl = -1
        if (self.left <= 0): self.dl = 1
        self.top += self.dt
        if (self.top >= self.max): self.dt = -1
        if (self.top <= 0): self.dt = 1
        self.right += self.dr
        if (self.right >= self.max): self.dr = -1
        if (self.right <= 0): self.dr = 1

    #@micropython.native
    def meterDraw(self):
        for i in range(0, len(self._screen)):
            self._screen[i] = 129
        if self.left <= 40:
            sl = 0
            fl = self.left
        else :
            sl = self.left - 40
            fl = 40
        for i in range(sl, fl):
            self._screen[36-i] = 0xff
            self._screen[36+i] = 0xff
        if self.top <= 40:
            st = 0
            ft = self.top
        else :
            st = self.top - 40
            ft = 40
        for i in range(st, ft):
            self._screen[116-i] = 0xff
            self._screen[116+i] = 0xff
        if self.right < 40:
            sr = 0
            fr = self.right
        else :
            sr = self.right - 40
            fr = 40
        for i in range(sr, ft):
            self._screen[196-i] = 0xff
            self._screen[196+i] = 0xff

    def __init__(self, screen):
        self._screen = screen
        self.max = 80
        self.left = 0
        self.dl = 1
        self.top = 0
        self.dt = 1
        self.right = 0
        self.dr = 1
        
    def draw(self):
        self.meterDraw()
        self.meterUpdate()
        return True
    
    def input(self, i):
        if i[0] != plugin.EVENT_JOYSTICK:
            return
        if i[1] == plugin.JOYSTICK_LEFT:
            if self._drawinterval > 1:
                self._drawinterval -= 1

        elif i[1] == plugin.JOYSTICK_RIGHT:
            self._drawinterval += 1
