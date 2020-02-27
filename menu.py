import pyglet as pgl


class Button:
    def __init__(self, x, y, image_name, scale, command, batch, window, anchor_x="center", anchor_y="center",
                 group=None, hidden=False):
        if type(image_name) == list:
            if len(image_name) == 2:
                self._images = [image_name, 0]
                self._curr_image = 0
                image_name = image_name[0]
            elif len(image_name) == 1:
                image_name = image_name[0]
            else:
                raise ValueError(f"Invalid amount of images! ({len(image_name)})")
        else:
            self._curr_image = None
            self._images = None

        self._x = x
        self._y = y
        self._anchor_x = anchor_x
        self._anchor_y = anchor_y
        self._opacity = 255
        self._command = command
        self._hidden = hidden
        self._scale = scale
        self._sprite = None
        self._batch = batch
        self._group = group
        self._window = window
        self._was_moused_over = False

        self._image, self._image_bounds = self._image_init(image_name, anchor_x, anchor_x)

        if not hidden:
            self._hidden = True
            self.show()

    def click(self, x, y):
        """run command if clicked"""
        if self._command is not None and not self._hidden:
            min_x, max_x, min_y, max_y = self._image_bounds

            if min_x < x < max_x and min_y < y < max_y:
                self._command()

                if self._images is not None:
                    self._image, self._image_bounds = self._image_init(self._images[0][1 - self._curr_image],
                                                                       self._anchor_x, self._anchor_y)
                    self._sprite.image = self._image
                    self._curr_image = 1 - self._curr_image

    def mouse_over(self, x, y):
        """set mouse cursor to hand when mouse over icon"""
        if self._command is not None and not self._hidden:
            min_x, max_x, min_y, max_y = self._image_bounds

            if min_x < x < max_x and min_y < y < max_y and not self._was_moused_over:
                cursor = self._window.get_system_mouse_cursor(self._window.CURSOR_HAND)
                self._window.set_mouse_cursor(cursor)
                self._was_moused_over = True

            elif (not min_x < x < max_x or not min_y < y < max_y) and self._was_moused_over:
                cursor = self._window.get_system_mouse_cursor(self._window.CURSOR_DEFAULT)
                self._window.set_mouse_cursor(cursor)
                self._was_moused_over = False

    def update_opacity(self, opacity, absolute=False):
        """update opacity of image"""
        if absolute:
            self._opacity = opacity
        else:
            self._sprite.opacity += opacity

    def hide(self):
        """remove image, disable click"""
        if not self._hidden:
            self._sprite.delete()
            self._sprite = None
            self._hidden = True

    def show(self):
        """re-enable image and click"""
        if self._hidden:
            self._sprite = pgl.sprite.Sprite(self._image, x=self._x, y=self._y, batch=self._batch, group=self._group)
            self._sprite.scale = self._scale
            self._sprite.opacity = self._opacity
            self._hidden = False

    def _image_init(self, image_name, anchor_x, anchor_y):
        image = pgl.resource.image(image_name)
        image_bounds = []

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

        if anchor_x == "center":
            image.anchor_y = image.height // 2
            image_bounds.extend(
                [self._y - (image.height // 2) * self._scale, self._y + (image.height // 2) * self._scale])
        elif anchor_x == "bottom":
            image.anchor_y = 0
            image_bounds.extend([self._y, self._y + image.height * self._scale])
        elif anchor_x == "top":
            image.anchor_y = image.height
            image_bounds.extend([y - image.width * self._scale, self._y])
        else:
            raise ValueError(f"Invalid anchor y: \"{anchor_y}\"")

        return image, image_bounds


class Menu:
    def __init__(self, window, batch, functions):
        self._main_x = int(window.width * 0.96)
        self._main_width = int(window.width * 0.04)

        self._colour_x = int(window.width * 0.845)
        self._colour_width = int(window.width * 0.112)

        self._height = window.height

        self._batch = batch

        self._main = False
        self._colour = False
        self._was_moused_over = False

        button_group = pgl.graphics.OrderedGroup(2)
        slider_group = pgl.graphics.OrderedGroup(3)

        # main menu setup
        self._main_opacity = 255
        self._main_primitives = None

        x = self._main_x + (self._main_width / 2)
        w = self._main_width
        self._main_buttons = []

        self._main_buttons.append(
            Button(x, self._height - (w * 0.6), ["pause.png", "play.png"], 0.24, functions["pause"], batch, window,
                   group=button_group, hidden=True))
        self._main_buttons.append(
            Button(x, self._height - (w * 1.6), "restart.png", 0.24, functions["reset"], batch, window,
                   group=button_group, hidden=True))

        self._main_buttons.append(
            Button(x, self._height - (w * 3), "fast.png", 0.24, None, batch, window,
                   group=button_group, hidden=True))

        self._main_buttons.append(
            Button(x, w * 3, "slow.png", 0.24, None, batch, window,
                   group=button_group, hidden=True))

        self._main_buttons.append(
            Button(x, (w * 1.7), ["counter_on.png", "counter_off.png"], 0.24, functions["toggle_counter"], batch,
                   window, group=button_group, hidden=True))
        self._main_buttons.append(
            Button(x, (w * 0.7), "settings.png", 0.24, self._toggle_colour, batch, window, group=button_group,
                   hidden=True))

        # colour menu setup
        self._colour_opacity = 255
        self._colour_primitives = None

        x = self._colour_x + (self._colour_width / 2)
        w = self._colour_width
        self._colour_buttons = []

        # x, y, image_name, scale, command, batch, window, anchor_x = "left", anchor_y = "bottom", group = None, hidden = False

    def click(self, x, y):
        """run click on all buttons in moused over section"""
        if self._main_x < x < self._main_x + self._main_width:
            for button in self._main_buttons:
                button.click(x, y)

            return True

        return False

    def mouse_over(self, x, y):
        """run mouse over on all buttons in moused over section"""
        if self._main_x < x < self._main_x + self._main_width:
            for button in self._main_buttons:
                button.mouse_over(x, y)
                self._was_moused_over = True

        elif self._was_moused_over:
            for button in self._main_buttons:
                button.mouse_over(x, y)
                self._was_moused_over = False

    def toggle_main(self):
        """toggle main menu"""
        if self._main:
            self.hide_main()
        else:
            self._show_main()

    def _update_main_opacity(self, do):
        """increase /  decrease main opacity"""
        if self._main:
            self._main_opacity += do

            if self._main_opacity > 255:
                self._main_opacity = 255

            elif self._main_opacity < 0:
                self._main_opacity = 0

            self._main_primitives[0].colors = [51, 51, 51, self._main_opacity] * 4
            self._main_primitives[1].colors = [76, 76, 76, self._main_opacity] * 4
            self._main_primitives[2].colors = [76, 76, 76, self._main_opacity] * 4
            self._main_primitives[3].colors = [76, 76, 76, self._main_opacity] * 4

    def _show_main(self):
        """display main menu"""
        if not self._main:
            self._main = True
            bg_group = pgl.graphics.OrderedGroup(1)
            divider_group = pgl.graphics.OrderedGroup(2)

            x, w, h = self._main_x, self._main_width, self._height

            self._main_primitives = []

            self._main_primitives.append(self._batch.add(4, pgl.gl.GL_QUADS, bg_group,
                                                         ("v2i", (x, 0, x, h, x + w, h, x + w, 0)),
                                                         ("c4B", ([51, 51, 51, self._main_opacity] * 4))))

            self._main_primitives.append(self._batch.add(4, pgl.gl.GL_QUADS, divider_group,
                                                         ("v2i", (x + 5, h - int(w * 2.3), x + 5, h - int(w * 2.3) + 2,
                                                                  x + w - 5, h - int(w * 2.3) + 2, x + w - 5,
                                                                  h - int(w * 2.3))),
                                                         ("c4B", ([76, 76, 76, self._main_opacity] * 4))))

            self._main_primitives.append(self._batch.add(4, pgl.gl.GL_QUADS, divider_group,
                                                         ("v2i", (
                                                         x + 5, int(w * 2.3), x + 5, int(w * 2.3) + 2, x + w - 5,
                                                         int(w * 2.3) + 2, x + w - 5, int(w * 2.3))),
                                                         ("c4B", ([76, 76, 76, self._main_opacity] * 4))))

            self._main_primitives.append(self._batch.add(4, pgl.gl.GL_QUADS, divider_group,
                                                         ("v2i", (
                                                         x + (w // 2) - 2, w * 4, x + (w // 2) - 2, h - (w * 4),
                                                         x + (w // 2) + 2, h - (w * 4), x + (w // 2) + 2, w * 4)),
                                                         ("c4B", ([76, 76, 76, self._main_opacity] * 4))))

            for button in self._main_buttons:
                button.show()

    def hide_main(self):
        """hide main menu"""
        if self._colour:
            self._hide_colour()

        if self._main:
            for item in self._main_primitives:
                item.delete()

            self._main_primitives = None

            for button in self._main_buttons:
                button.hide()

            self._main = False

    def _toggle_colour(self):
        """toggle colour menu"""
        if self._colour:
            self._hide_colour()
        else:
            self._show_colour()

    def _show_colour(self):
        """show colour menu"""
        if not self._colour:
            self._colour = True
            bg_group = pgl.graphics.OrderedGroup(1)
            divider_group = pgl.graphics.OrderedGroup(2)

            x, w, h = self._colour_x, self._colour_width, self._height
            print(x, w)

            self._colour_primitives = []

            self._colour_primitives.append(self._batch.add(4, pgl.gl.GL_QUADS, bg_group,
                                                           ("v2i", (x, 0, x, h, x + w, h, x + w, 0)),
                                                           ("c4B", ([51, 51, 51, self._main_opacity] * 4))))

    def _hide_colour(self):
        """hide colour menu"""
        if self._colour:
            for item in self._colour_primitives:
                item.delete()

            self._colour_primitives = None

            for button in self._colour_buttons:
                button.hide()

            self._colour = False

    def add_colour_group(self):
        pass

    def remove_colour_group(self, index):
        pass

    def reset_colours(self):
        pass
