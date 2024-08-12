import plugin
import random

class plugin_visual:
    _name = 'cgol'
    _drawinterval = 1
    _init_random_cells = True

    @micropython.native
    def draw(self):
        if self._init_random_cells:
            for i in range(0, len(self._screen)):
                self._screen[i] = random.getrandbits(8)
            self._init_random_cells = False
        for i in range(0, len(self._screen)-1):
            for pos in range(0,8):
                liveNeighbors = self.getLiveNeighbors(i, pos)
                if liveNeighbors < 2:
                    self._screen[i] = self._screen[i] & ~(1 << pos)
                if liveNeighbors > 3:
                    self._screen[i] = self._screen[i] & ~(1 << pos)
                if (self._screen[i] >> pos) & 1 == 0 and liveNeighbors == 3:
                    self._screen[i] = self._screen[i] | (1 << pos)
        if random.random() < .1: # destabilize
            i = random.randint(1, len(self._screen)-2)
            self._screen[i-1] = random.getrandbits(8)
            self._screen[i] = random.getrandbits(8)
            self._screen[i+1] = random.getrandbits(8)
        return True
    
    
    # @micropython.native
    def getLiveNeighbors(self, i, pos):
        liveNeighbors = 0
        i = i % 240
        if pos < 7 and 2**(pos+1) & self._screen[i-1] == 2**(pos+1):
            liveNeighbors += 1
        if pos < 7 and 2**(pos+1) & self._screen[i] == 2**(pos+1):
            liveNeighbors += 1
        if pos < 7 and 2**(pos+1) & self._screen[i+1] == 2**(pos+1):
            liveNeighbors += 1
        if 2**pos & self._screen[i-1] == 2**pos:
            liveNeighbors += 1
        if 2**pos & self._screen[i+1] == 2**pos:
            liveNeighbors += 1
        if pos > 0 and 2**(pos-1) & self._screen[i-1] == 2**(pos-1):
            liveNeighbors += 1
        if pos > 0 and 2**(pos-1) & self._screen[i] == 2**(pos-1):
            liveNeighbors += 1
        if pos > 0 and 2**(pos-1) & self._screen[i+1] == 2**(pos-1):
            liveNeighbors += 1
        return liveNeighbors


    def __init__(self, screen):
        self._screen = screen
        

    def input(self, i):
        if i[0] == plugin.EVENT_JOYSTICK and i[1] in [ plugin.JOYSTICK_UP, plugin.JOYSTICK_DOWN, plugin.JOYSTICK_LEFT, plugin.JOYSTICK_RIGHT ]:
            self._init_random_cells = True




