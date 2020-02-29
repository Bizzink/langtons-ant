import pyglet as pgl
from pyglet.window import key, mouse
import menu
from grid import Grid
from ant import Ant


# menu functions
def toggle_pause():
    global paused
    if paused:
        paused = False
    else:
        paused = True


def reset():
    global grid, ant
    grid.delete()
    del grid
    del ant

    grid = Grid([5, 5], rules, batch, window, scale=25)
    ant = Ant(2, 2, grid)


def toggle_counter():
    global counter

    if counter is not None:
        counter.delete()
        counter = None

    else:
        counter = pgl.text.Label(text="", x=20, y=20, font_size=20, font_name="Gotham", color=[255, 255, 255, 100],
                                 batch=batch, group=pgl.graphics.OrderedGroup(1))


window = pgl.window.Window(1920, 1080)
batch = pgl.graphics.Batch()

# for transparent primitives
pgl.gl.glEnable(pgl.gl.GL_BLEND)
pgl.gl.glBlendFunc(pgl.gl.GL_SRC_ALPHA, pgl.gl.GL_ONE_MINUS_SRC_ALPHA)

pgl.resource.path = ["resources"]
pgl.resource.reindex()
pgl.resource.add_font("Gotham-Bold.otf")

rules = []

menu_functions = {"pause": toggle_pause,
                  "reset": reset,
                  "toggle_counter": toggle_counter}

menu = menu.init(window, batch, menu_functions, rules)
grid = Grid([5, 5], rules, batch, window, scale=25)
ant = Ant(2, 2, grid)

prev_highlight = None
paused = True
dragged = False
counter = None
mouse_menu = False
drag_x = drag_y = 0


@window.event
def on_key_press(symbol, mod):
    if symbol == key.SPACE:
        menu.toggle()


@window.event
def on_mouse_motion(x, y, dx, dy):
    global prev_highlight, mouse_menu

    if prev_highlight is not None:
        prev_highlight.highlight(reset=True)

    tile = grid.get_tile(x, y)
    prev_highlight = tile

    if tile is not None:
        tile.highlight()

    mouse_menu = menu.mouse_over(x, y)


@window.event
def on_mouse_drag(x, y, dx, dy, button, mods):
    global dragged, drag_x, drag_y, mouse_menu

    if button == mouse.LEFT:
        if mouse_menu:
            # menu.drag(dx, dy)
            pass
        else:
            drag_x += dx
            drag_y += dy
            dragged = True


@window.event
def on_mouse_release(x, y, button, mods):
    global dragged

    if button == mouse.LEFT:
        if not dragged:
            menu.click()

        dragged = False


@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    grid.scale(x, y, scroll_y)


@window.event
def on_draw():
    window.clear()
    batch.draw()


def update(dt):
    global drag_x, drag_y, paused, counter

    if not paused:
        ant.update()

    if counter is not None:
        counter.text = f"Step: {ant.get_steps()}"

    grid.move(drag_x, drag_y)
    drag_x = drag_y = 0


if __name__ == '__main__':
    pgl.clock.schedule_interval(update, 1 / 120)
    pgl.app.run()
