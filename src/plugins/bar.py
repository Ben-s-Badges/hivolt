import plugin

class plugin_visual:
    _name = 'bar'
    _drawinterval = 10

    @micropython.native
    def draw(self):
        self._offset = (self._offset + 1) % plugin.SCREEN_SIZE
        for i in range(0,plugin.SCREEN_SIZE):
            self._screen[i] = 0

        self._screen[self._offset] = 0xff
        self._screen[(self._offset + 1) % plugin.SCREEN_SIZE] = 0xff
        self._screen[(self._offset + 2) % plugin.SCREEN_SIZE] = 0xff
        self._screen[(self._offset + 3) % plugin.SCREEN_SIZE] = 0xff

        self._screen[(self._offset + 80) % plugin.SCREEN_SIZE] = 0xff
        self._screen[(self._offset + 81) % plugin.SCREEN_SIZE] = 0xff
        self._screen[(self._offset + 82) % plugin.SCREEN_SIZE] = 0xff
        self._screen[(self._offset + 83) % plugin.SCREEN_SIZE] = 0xff

        self._screen[(self._offset + 160) % plugin.SCREEN_SIZE] = 0xff
        self._screen[(self._offset + 161) % plugin.SCREEN_SIZE] = 0xff
        self._screen[(self._offset + 162) % plugin.SCREEN_SIZE] = 0xff
        self._screen[(self._offset + 163) % plugin.SCREEN_SIZE] = 0xff
        return True

    def __init__(self, screen):
        self._screen = screen
        self._offset = 0

    def input(self, i):
        pass
