import plugin

class plugin_visual:
    _name = 'meter'
    _drawinterval = 5

    #@micropython.native
    def meterUpdate(self):
        if self.mode == 0:
            self.left += self.dl
            if (self.left >= self.max): self.dl = -1
            if (self.left <= 0): self.dl = 1
            self.top += self.dt
            if (self.top >= self.max): self.dt = -1
            if (self.top <= 0): self.dt = 1
            self.right += self.dr
            if (self.right >= self.max): self.dr = -1
            if (self.right <= 0): self.dr = 1
        if self.mode == 1:
            x = 0.0
            y = 0.0
            z = 0.0
            for i in range (0, len(self.xyz)):
                x = x + self.xyz[i][0]
                y = y + self.xyz[i][1]
                z = z + self.xyz[i][2]
            x = x / len(self.xyz)
            y = y / len(self.xyz)
            z = z / len(self.xyz)
            self.left = int(x * 40.0)
            if self.left < 0:
                self.left = self.left + 80
            if self.left < 0:
                self.left = 0
            if self.left > 80:
                self.left = 80
            self.top = int(y * 40.0)
            if self.top < 0:
                self.top = self.top + 80
            if self.top < 0:
                self.top = 0
            if self.top > 80:
                self.top = 80
            self.right = int(z * 40.0)
            if self.right < 0:
                self.right = self.right + 80
            if self.right < 0:
                self.right = 0
            if self.right > 80:
                self.right = 80

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
            m = 36-i
            if m < 0:
                m = 0
            self._screen[m] = 0xff
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
            p = 196+i
            if p > 239:
                p = 239
            self._screen[196-i] = 0xff
            self._screen[p] = 0xff

    def __init__(self, screen):
        self._screen = screen
        self.max = 80
        self.left = 0
        self.dl = 1
        self.top = 0
        self.dt = 1
        self.right = 0
        self.dr = 1
        self.mode = 0
        self.xyz = [(0.0, 0.0, 0.0),
                    (0.0, 0.0, 0.0),
                    (0.0, 0.0, 0.0),
                    (0.0, 0.0, 0.0),
                    (0.0, 0.0, 0.0),
                    (0.0, 0.0, 0.0),
                    (0.0, 0.0, 0.0),
                    (0.0, 0.0, 0.0),
                    (0.0, 0.0, 0.0),
                    (0.0, 0.0, 0.0)]
        
    def draw(self):
        self.meterDraw()
        self.meterUpdate()
        return True
    
    def input(self, i):
        if i[0] == plugin.EVENT_JOYSTICK:
            if i[1] == plugin.JOYSTICK_LEFT:
                if self._drawinterval > 1:
                    self._drawinterval -= 1

            elif i[1] == plugin.JOYSTICK_RIGHT:
                self._drawinterval += 1

            elif i[1] == plugin.JOYSTICK_UP:
                if self.mode == 0:
                    print("Switching to accelerometer mode")
                    self.mode = 1
                else:
                    print("Switching to normal mode")
                    self.mode = 0

        if i[0] == plugin.EVENT_ACCEL:
            xyz = i[1]
            x = xyz[0] % 1
            y = xyz[1] % 1
            z = xyz[2] % 1
            self.xyz.pop(0)
            self.xyz.insert(len(self.xyz)-1, (x, y, z))
            #print("Accel %d, %d, %d", xyz[0], xyz[1], xyz[2])

