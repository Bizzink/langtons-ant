import pyglet as pgl


g = None


class Globals:
    def __init__(self, batch, window):
        self.batch = batch
        self.window = window


def init(batch, window):
    global g
    g = Globals(batch, window)


class Slider:
    def __init__(self, cx, cy, length, scale, min_val, max_val, default_val, orientation, group):
        self._cx = cx
        self._cy = cy
        self._length = length
        self._value = default_val
        self._min_val = min_val
        self._max_val = max_val
        self._orientation = orientation
        self._hidden = True
        self._moused_over = False

        handle_image = pgl.resource.image("slider.png")
        handle_image.anchor_x = handle_image.width / 2
        handle_image.anchor_y = handle_image.height / 2

        self._sprite = pgl.sprite.Sprite(handle_image, x=cx, y=cx, batch = g.batch, group = group)
        self._sprite.scale = scale
        self._sprite.visible = False

        # pos = val / (max_val - min_val) * length
        # val = pos / length * (max_val - min_val)

        if orientation == "vertical":
            self._sprite.y = cy - (length / 2) + default_val / (max_val - min_val) * length
        elif orientation == "horizontal":
            self._sprite.x = cx - (length / 2) + default_val / (max_val - min_val) * length
            self._sprite.rotation = 90
        else:
            raise ValueError(f"Invalid orientation \"{orientation}\"")

    def drag(self, dx, dy):
        if self._moused_over:
            if self._orientation == "vertical":
                drag = dy
            else:
                drag = dx

            self._value += drag / self._length * (self._max_val - self._min_val)

            if self._value < self._min_val: self._value = self._min_val
            if self._value > self._max_val: self._value = self._max_val

            pos = self._value / (self._max_val - self._min_val) * self._length

            if self._orientation == "vertical":
                self._sprite.y = self._cy - (self._length / 2) + pos - self._sprite.height / 2
            else:
                self._sprite.x = self._cx - (self._length / 2) + pos - self._sprite.width / 2

    def mouse_over(self, x, y):
        if not self._hidden:
            min_x = self._sprite.x - self._sprite.width / 2
            max_x = self._sprite.x + self._sprite.width / 2
            min_y = self._sprite.y - self._sprite.height / 2
            max_y = self._sprite.y + self._sprite.height / 2

            if min_x < x < max_x and min_y < y < max_y and not self._moused_over:
                cursor = g.window.get_system_mouse_cursor(g.window.CURSOR_HAND)
                g.window.set_mouse_cursor(cursor)
                self._moused_over = True

            elif (not min_x < x < max_x or not min_y < y < max_y) and self._moused_over:
                cursor = g.window.get_system_mouse_cursor(g.window.CURSOR_DEFAULT)
                g.window.set_mouse_cursor(cursor)
                self._moused_over = False

    def show(self):
        self._sprite.visible = True
        self._hidden = False

    def hide(self):
        self._sprite.visible = False
        self._hidden = True
