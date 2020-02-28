import pyglet as pgl
import colorsys


g = None


class Globals:
    def __init__(self, batch, window):
        self.batch = batch
        self.window = window


def init(batch, window):
    global g
    g = Globals(batch, window)


class ColourPick:
    def __init__(self, x, y, current_colour):
        pass

    def mouse_over(self, x, y):
        pass

    def mouse_drag(self, x, y, dx, dy):
        pass

    def delete(self):
        pass