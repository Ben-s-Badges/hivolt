import plugin

class plugin_visual:
    _name = 'pulse'
    _drawinterval = 25

    def draw(self):
        if (self._offset >> 3) == 0:
            bit = 1 << self._offset
        else:
            bit = 0x80 >> (self._offset&0x7)
        self._offset = (self._offset + 1) % 16

        for i in range(0, plugin.SCREEN_SIZE):
            self._screen[i] = bit
            
        return True

    def __init__(self, screen):
        self._screen = screen
        self._offset = 0

    def input(self, i):
        pass
