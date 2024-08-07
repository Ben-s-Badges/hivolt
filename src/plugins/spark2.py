import plugin
import random

SIZE = 240
class plugin_visual:
    _name = 'spark2'
    _drawinterval = 25

    @micropython.native
    def randomise(self, v):
        r = random.getrandbits(8)
        p = random.getrandbits(1)
        d = r
        if (p):
            d = -d
        if ((v+d) <= 0):
            d = 256
        if ((v+d) >= 2048):
            d = -256
        v += d
        return v
    
    @micropython.native
    def sparkUpdate(self):
        v = self.values[0]
        self.values[0] = self.randomise(v)
        for i in range(1,SIZE/2):
            v = self.randomise(v)
            self.values[i] = v

    @micropython.native
    def sparkDraw(self):
        self.sparkUpdate()
        for i in range(0,SIZE/2):
            v = self.values[i]>>8
            self._screen[i] = (1<<v)
            self._screen[(SIZE-1) - i] = (1<<v)

    def __init__(self, screen):
        self._screen = screen
        self.values = []
        v = random.getrandbits(3 + 8)
        for i in range(0, SIZE/2):
            self.values.append(v)
            v = self.randomise(v)
            
    def draw(self):
        self.sparkDraw()
        return True

    def input(self, i):
        pass

