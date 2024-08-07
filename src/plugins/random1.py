import plugin
import random

class plugin_visual:
    _name = 'random1'
    _drawinterval = 10

    @micropython.native
    def draw(self):
        for i in range(0, len(self._screen)):
            self._screen[i] = random.getrandbits(8)        
        return True

    def __init__(self, screen):
        self._screen = screen

    def input(self, i):
        pass
