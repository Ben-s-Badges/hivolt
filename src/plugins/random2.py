import plugin
import random

class plugin_visual:
    _name = 'random2'
    _drawinterval = 1

    def draw(self):
        self._offset = (self._offset + 1) % len(self._screen)
        self._screen[self._offset] = random.getrandbits(8)
        return True

    def __init__(self, screen):
        self._screen = screen
        self._offset = 0

    def input(self, i):
        pass
