import plugin
import random

SIZE = 240
class plugin_visual:
    _name = 'bounce'
    _drawinterval = 1

    @micropython.native
    def Update(self):
        for i in range(1, self.count):
            x = self.values[(i*4)+0]
            dx = self.values[(i*4)+1]
            y = self.values[(i*4)+2]
            dy = self.values[(i*4)+3]
            x += dx
            if x <= 0:
                x += (SIZE-1)<<8
            if x >= (SIZE-1)<<8:
                x -= (SIZE-1)<<8
            y += dy
            if y <= 0:
                y = 0
                dy = -dy
            if y >= 7<<8:
                y = 7<<8
                dy = -dy
            self.values[(i*4)+0] = x
            self.values[(i*4)+1] = dx
            self.values[(i*4)+2] = y
            self.values[(i*4)+3] = dy

    @micropython.native
    def Draw(self):
        self.Update()
        for i in range(0,SIZE):
            self._screen[i] = 0
        for i in range(1, self.count):
            x = self.values[(i*4)+0]
            y = self.values[(i*4)+2]
            self._screen[x>>8] = self._screen[x>>8] | (1<<(y>>8))
        

    def __init__(self, screen):
        self._screen = screen
        self.count = 32
        self.values = []
        for i in range(0, self.count):
            x = random.randrange((SIZE-1)<<8)
            dx = random.randrange(-128, 128)
            y = random.randrange(7<<8)
            dy = random.randrange(-128, 128)
            self.values.append(x)
            self.values.append(dx)
            self.values.append(y)
            self.values.append(dy)
            
    def draw(self):
        self.Draw()
        return True

    def input(self, i):
        pass

