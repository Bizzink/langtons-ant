import pyglet as pgl
from pyglet.window import key
from grid import Grid

window = pgl.window.Window(1280, 720)
batch = pgl.graphics.Batch()

colour_orders = [{"col": [255, 0, 0], "dir": 1},
                 {"col": [255, 255, 255], "dir": -1}]

test = Grid([100, 100], [20, 5], colour_orders, batch, scale = 25)


@window.event
def on_key_press(symbol, mod):
    if symbol == key.SPACE:
        pass


@window.event
def on_mouse_drag(x ,y ,dx ,dy , buttons, mods):
    test.move(dx, dy)


@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    test.scale(scroll_y)


@window.event
def on_draw():
    window.clear()
    batch.draw()


if __name__ == '__main__':
    pgl.app.run()
