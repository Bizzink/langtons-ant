import pyglet as pgl


g = None


class Globals:
    def __init__(self, batch, window):
        self.batch = batch
        self.window = window


def init(batch, window):
    global g
    g = Globals(batch, window)


class Button:
    def __init__(self, x, y, image_name, scale, command, anchor_x="center", anchor_y="center",
                 group=pgl.graphics.OrderedGroup(2), hidden=True):
        self._x = x
        self._y = y
        self._anchor_x = anchor_x
        self._anchor_y = anchor_y
        self._opacity = 255
        self._command = command
        self._hidden = hidden
        self._scale = scale

        self._group = group
        self._moused_over = False

        self._image = image_name
        self._curr_image = 0

        if type(image_name) != list:
            image_name = [image_name]

        image, self._image_bounds = self._image_init(image_name[0])
        self._sprite = pgl.sprite.Sprite(image, x = x, y = y, batch = g.batch, group = group)
        self._sprite.scale = scale

        if hidden:
            self._sprite.visible = False

    def __str__(self):
        return self._image

    def click(self):
        """run command if clicked"""
        if self._command is not None and not self._hidden and self._moused_over:
            if type(self._command) == list:
                for command in self._command:
                    command()
            else:
                self._command()

            if type(self._image) == list:
                image, self._image_bounds = self._image_init(self._image[1 - self._curr_image])
                self._sprite.image = image
                self._curr_image = 1 - self._curr_image

    def mouse_over(self, x, y):
        """set mouse cursor to hand when mouse over icon"""
        if self._command is not None and not self._hidden:
            min_x, max_x, min_y, max_y = self._image_bounds

            if min_x < x < max_x and min_y < y < max_y and not self._moused_over:
                cursor = g.window.get_system_mouse_cursor(g.window.CURSOR_HAND)
                g.window.set_mouse_cursor(cursor)
                self._moused_over = True

            elif (not min_x < x < max_x or not min_y < y < max_y) and self._moused_over:
                cursor = g.window.get_system_mouse_cursor(g.window.CURSOR_DEFAULT)
                g.window.set_mouse_cursor(cursor)
                self._moused_over = False

    def update_opacity(self, opacity, absolute=False):
        """update opacity of image"""
        if absolute:
            self._opacity = opacity
        else:
            self._sprite.opacity += opacity

        if self._opacity > 255:
            self._opacity = 255

        elif self._opacity < 0:
            self._opacity = 0

        if not self._hidden:
            self._sprite.opacity = opacity

    def hide(self):
        """hide sprite, disable click"""
        self._sprite.visible = False
        self._hidden = True

    def show(self):
        """show sprite, enable click"""
        self._sprite.visible = True
        self._hidden = False

    def tint(self, colour, reset = False):
        """tint sprite"""
        if reset:
            self._sprite.color = (255, 255, 255)

        else:
            self._sprite.color = colour

    def flip(self, flipped):
        """flip sprite horizontally"""
        if flipped:
            self._sprite.scale_x = -1
        else:
            self._sprite.scale_x = 1

    def _image_init(self, image_name):
        image = pgl.resource.image(image_name)
        image_bounds = []
        anchor_x, anchor_y = self._anchor_x, self._anchor_y

        if anchor_x == "center":
            image.anchor_x = image.width // 2
            image_bounds.extend([self._x - image.width // 2 * self._scale, self._x + (image.width // 2) * self._scale])
        elif anchor_x == "left":
            image.anchor_x = 0
            image_bounds.extend([self._x, self._x + image.width * self._scale])
        elif anchor_x == "right":
            image.anchor_x = image.width
            image_bounds.extend([self._x - image.width * self._scale, self._x])
        else:
            raise ValueError(f"Invalid anchor x: \"{anchor_x}\"")

        if anchor_y == "center":
            image.anchor_y = image.height // 2
            image_bounds.extend(
                [self._y - (image.height // 2) * self._scale, self._y + (image.height // 2) * self._scale])
        elif anchor_y == "bottom":
            image.anchor_y = 0
            image_bounds.extend([self._y, self._y + image.height * self._scale])
        elif anchor_y == "top":
            image.anchor_y = image.height
            image_bounds.extend([self._y - image.width * self._scale, self._y])
        else:
            raise ValueError(f"Invalid anchor y: \"{anchor_y}\"")

        return image, image_bounds
