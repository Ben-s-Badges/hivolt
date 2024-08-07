import plugin

class plugin_visual:
    _name = 'wipe'
    _drawinterval = 4

    @micropython.native
    def draw(self):
        self._offset = (self._offset + 1) % plugin.SCREEN_SIZE

        self._screen[(self._offset +   0) % plugin.SCREEN_SIZE] = 0xff
        self._screen[(self._offset +  80) % plugin.SCREEN_SIZE] = 0xff
        self._screen[(self._offset + 160) % plugin.SCREEN_SIZE] = 0xff

        if self._offset >= (plugin.SCREEN_SIZE/2):
            clr = 40
            self._screen[(self._offset + clr +   0) % plugin.SCREEN_SIZE] = 0
            self._screen[(self._offset + clr +  80) % plugin.SCREEN_SIZE] = 0
            self._screen[(self._offset + clr + 160) % plugin.SCREEN_SIZE] = 0

        return True

    def __init__(self, screen):
        self._screen = screen
        self._offset = 0

    def input(self, i):
        pass
