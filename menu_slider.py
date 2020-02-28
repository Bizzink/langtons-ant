import pyglet as pgl


class Slider:
    def __init__(self, cx, cy, width, length, min_val, max_val, default_val, orientation, batch, group):
        self._cx = cx
        self._cy = cy
        self._width = width
        self._length = length