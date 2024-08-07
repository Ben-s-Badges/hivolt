import plugin
import random

SIZE = 240
class plugin_visual:
    _name = 'stars'
    _drawinterval = 1
    
    @micropython.native
    def Update(self):
        for i in range(1, self.count):
            x = self.values[(i*3)+0]
            dx = self.values[(i*3)+1]
            x += dx
            if x <= 0:
                x += (SIZE-1)<<8
            if x >= (SIZE-1)<<8:
                x -= (SIZE-1)<<8
            self.values[(i*3)+0] = x
            self.values[(i*3)+1] = dx

    @micropython.native
    def Draw(self):
        self.Update()
        for i in range(0,SIZE):
            self._screen[i] = 0
        for i in range(1, self.count):
            x = self.values[(i*3)+0]
            y = self.values[(i*3)+2]
            self._screen[x>>8] = self._screen[x>>8] | (1<<(y>>8))
        

    def __init__(self, screen):
        self._screen = screen
        self.count = 128
        self.values = []
        for i in range(0, self.count):
            x = random.randrange((SIZE-1)<<8)
            dx = random.randrange(16, 128)
            y = random.randrange(8<<8)
            self.values.append(x)
            self.values.append(dx)
            self.values.append(y)
            
    def draw(self):
        self.Draw()
        return True

    def input(self, i):
        pass

