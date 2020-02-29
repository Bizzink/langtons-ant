import pyglet as pgl


g = None


class Globals:
    def __init__(self, batch, window):
        self.batch = batch
        self.window = window


def init(batch, window):
    global g
    g = Globals(batch, window)


def image_init(image_name):
    """set up image for sprite"""
    image = pgl.resource.image(image_name)
    image.anchor_x = image.width / 2
    image.anchor_y = image.height / 2
    return image


def set_cursor(cursor_type):
    """set mouse cursor"""
    if cursor_type == "hand": cursor = g.window.get_system_mouse_cursor(g.window.CURSOR_HAND)
    elif cursor_type == "default": cursor = g.window.get_system_mouse_cursor(g.window.CURSOR_DEFAULT)
    else: raise ValueError(f"Invalid cursor type \"{cursor_type}\"!")

    g.window.set_mouse_cursor(cursor)


class Button(pgl.sprite.Sprite):
    def __init__(self, image_names: list, commands: list, scale: float, clickable: bool = True, **kwargs):
        self._images = image_names
        self._commands = commands
        self._img_ind = 0
        self.moused_over = False
        self.clickable = clickable

        super().__init__(image_init(image_names[0]), **kwargs)
        self.batch = g.batch
        self.scale = scale
        self.visible = False
        if self.group is None: self.group = pgl.graphics.OrderedGroup(2)

    def click(self):
        if self.clickable and self.visible and self.moused_over:
            for command in self._commands: command()

            if len(self._images) > 1:
                self.image = image_init(self._images[1 - self._img_ind])
                self._img_ind = 1 - self._img_ind

    def mouse_over(self, x, y):
        """return true if x, y is in sprite bounds, change mouse cursor to hand"""
        if self.clickable:
            min_x = self.x - self.width / 2
            max_x = self.x + self.width / 2
            min_y = self.y - self.height / 2
            max_y = self.y + self.height / 2

            if min_x < x < max_x and min_y < y < max_y and not self.moused_over:
                set_cursor("hand")
                self.moused_over = True

            elif (not min_x < x < max_x or not min_y < y < max_y) and self.moused_over:
                set_cursor("default")
                self.moused_over = False
