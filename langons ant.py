import pyglet as pgl
from pyglet.window import key, mouse
from grid import Grid
from ant import Ant

window = pgl.window.Window(1920, 1080)
batch = pgl.graphics.Batch()

# for transparent primitives
pgl.gl.glEnable(pgl.gl.GL_BLEND)
pgl.gl.glBlendFunc(pgl.gl.GL_SRC_ALPHA, pgl.gl.GL_ONE_MINUS_SRC_ALPHA)

colour_orders = [{"col": [255, 255, 255], "dir": "left"},
                 {"col": [255, 0, 0], "dir": "right"}]

grid = Grid([5, 5], colour_orders, batch, window, scale=25)
ant = Ant(2, 2, grid)

prev_highlight = None
dragged = False


@window.event
def on_key_press(symbol, mod):
    if symbol == key.F3:
        pass


@window.event
def on_mouse_motion(x, y, dx, dy):
    global prev_highlight

    if prev_highlight is not None:
        prev_highlight.highlight(reset=True)

    tile = grid.get_tile(x, y)
    prev_highlight = tile

    if tile is not None:
        tile.highlight()


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, mods):
    global dragged
    grid.move(dx, dy)
    dragged = True


@window.event
def on_mouse_release(x, y, button, mods):
    pass

    global dragged

    if button == mouse.LEFT:
        if not dragged:
            row, col = grid.get_tile(x, y, get_ind=True)
            ants.append(Ant(row, col, grid))

        dragged = False


@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    grid.scale(x, y, scroll_y)


@window.event
def on_draw():
    window.clear()
    batch.draw()


def update(dt):
    ant.update()


if __name__ == '__main__':
    pgl.clock.schedule_interval(update, 1 / 120)
    pgl.app.run()
