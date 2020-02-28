import pyglet as pgl
import menu_button
import menu_rule
import menu_slider
from menu_button import Button
from menu_rule import Rule
from menu_slider import Slider


class Menu:
    def __init__(self, window, batch, functions, rule_list):
        button_scale = 0.24
        menu_button.init(batch, window)
        menu_slider.init(batch, window)
        menu_rule.init(batch, rule_list, button_scale, pgl.graphics.OrderedGroup(2), window)

        self._height = window.height
        self._was_moused_over = False
        self._batch = batch
        self._window = window

        # main menu setup
        self._main_x = int(window.width * 0.96)
        self._main_width = int(window.width * 0.04)
        self._main_opacity = 255
        self._main_primitives = None
        self._main_buttons = []
        self._main = False

        x = self._main_x + (self._main_width / 2)
        w = self._main_width

        self._main_buttons.append(
            Button(x, self._height - (w * 0.6), ["pause.png", "play.png"], button_scale, functions["pause"]))
        self._main_buttons.append(
            Button(x, self._height - (w * 1.6), "restart.png", button_scale, functions["reset"]))
        self._main_buttons.append(Button(x, self._height - (w * 3), "fast.png", button_scale, None))
        self._main_buttons.append(Button(x, w * 3, "slow.png", button_scale, None))
        self._main_buttons.append(
            Button(x, w * 1.7, ["counter_on.png", "counter_off.png"], button_scale, functions["toggle_counter"]))
        self._main_buttons.append(Button(x, (w * 0.7), "settings.png", button_scale,
                                         [self._toggle_rule, functions["pause"]]))

        self._speed_slider = Slider(x, self._height * 0.48, self._height - (w * 8), button_scale, 1, 10, 7, "vertical", pgl.graphics.OrderedGroup(2))

        # rule menu setup

        self._rule_x = int(window.width * 0.845)
        self._rule_width = int(window.width * 0.112)
        self._rule_opacity = 255
        self._rule_primitives = None
        self._rule_buttons = []
        self._rules = []
        self._rule = False

        x = self._rule_x + (self._rule_width / 2)
        w = self._rule_width
        h = self._height

        self._rule_buttons.append(Button(x, h * 0.05, "reset.png", button_scale, None))

        self._rules.append(Rule(x, h * 0.925, w, 0, permanent=True))
        self._rules.append(Rule(x, h * 0.85, w, 1, permanent=True, flipped=True))

    def click(self, x, y):
        """pass click event to buttons in moused over section"""
        # click main buttons
        if self._main_x < x < self._main_x + self._main_width:
            for button in self._main_buttons:
                button.click()
            return True

        # click rule buttons
        elif self._rule_x < x < self._rule_x + self._rule_width:
            for button in self._rule_buttons:
                button.click()
            for rule in self._rules:
                rule.click(x, y)
            return True

        return False

    def mouse_over(self, x, y):
        """pass mouse over event to buttons in moused over section"""
        # check moue over for main buttons
        if self._main and self._main_x < x < self._main_x + self._main_width:
            self._speed_slider.mouse_over(x, y)

            for button in self._main_buttons:
                button.mouse_over(x, y)
                self._was_moused_over = True

            return True

        # check mouse over for rule buttons
        elif self._rule and self._rule_x < x < self._rule_x + self._rule_width:
            for button in self._rule_buttons:
                button.mouse_over(x, y)
            for rule in self._rules:
                rule.mouse_over(x, y)

            return True

        # update on mouse leave to reset cursor
        elif self._was_moused_over:
            for button in self._main_buttons:
                button.mouse_over(x, y)
                self._was_moused_over = False

        return False

    def drag(self, dx, dy):
        if self._main:
            self._speed_slider.drag(dx, dy)

    def toggle_main(self):
        """toggle main menu"""
        if self._main:
            self.hide_main()
        else:
            self._show_main()

    def _update_main_opacity(self, opacity, absolute = False):
        """set main opacity"""
        if absolute:
            self._main_opacity = opacity
        else:
            self._main_opacity += opacity

        if self._main_opacity > 255:
            self._main_opacity = 255

        elif self._main_opacity < 0:
            self._main_opacity = 0

        if self._main:
            for primitive in self._main_primitives:
                colour = primitive.colors[:3].copy()
                colour.append(self._main_opacity)
                primitive.colors = colour * 4

        for button in self._main_buttons:
            button.update_opacity(self._main_opacity)

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
                                                         ("v2i", (x + 5, h - int(w * 2.3),
                                                                  x + 5, h - int(w * 2.3) + 2,
                                                                  x + w - 5, h - int(w * 2.3) + 2,
                                                                  x + w - 5, h - int(w * 2.3))),
                                                         ("c4B", ([76, 76, 76, self._main_opacity] * 4))))

            self._main_primitives.append(self._batch.add(4, pgl.gl.GL_QUADS, divider_group,
                                                         ("v2i", (
                                                             x + 5, int(w * 2.3),
                                                             x + 5, int(w * 2.3) + 2,
                                                             x + w - 5, int(w * 2.3) + 2,
                                                             x + w - 5, int(w * 2.3))),
                                                         ("c4B", ([76, 76, 76, self._main_opacity] * 4))))

            self._main_primitives.append(self._batch.add(4, pgl.gl.GL_QUADS, divider_group,
                                                         ("v2i", (
                                                             x + (w // 2) - 2, w * 4,
                                                             x + (w // 2) - 2, h - (w * 4),
                                                             x + (w // 2) + 2, h - (w * 4),
                                                             x + (w // 2) + 2, w * 4)),
                                                         ("c4B", ([76, 76, 76, self._main_opacity] * 4))))

            for button in self._main_buttons:
                button.show()

            self._speed_slider.show()

    def hide_main(self):
        """hide main menu"""
        if self._rule:
            self._hide_rule()

        if self._main:
            for item in self._main_primitives:
                item.delete()

            self._main_primitives = None

            for button in self._main_buttons:
                button.hide()

            cursor = self._window.get_system_mouse_cursor(self._window.CURSOR_DEFAULT)
            self._window.set_mouse_cursor(cursor)

            self._speed_slider.hide()

            self._main = False

    def _toggle_rule(self):
        """toggle rule menu"""
        if self._rule:
            self._hide_rule()
        else:
            self._show_rule()

    def _show_rule(self):
        """show rule menu"""
        if not self._rule:
            self._rule = True
            bg_group = pgl.graphics.OrderedGroup(1)
            arrow_group = pgl.graphics.OrderedGroup(2)

            x, w, h = self._rule_x, self._rule_width, self._height

            self._rule_primitives = []

            self._rule_primitives.append(self._batch.add(4, pgl.gl.GL_QUADS, bg_group,
                                                         ("v2i", (x, 0, x, h, x + w, h, x + w, 0)),
                                                         ("c4B", ([51, 51, 51, self._main_opacity] * 4))))
            for button in self._rule_buttons:
                button.show()
            for rule in self._rules:
                rule.show()

    def _hide_rule(self):
        """hide rule menu"""
        if self._rule:
            for item in self._rule_primitives:
                item.delete()

            self._rule_primitives = None

            for button in self._rule_buttons:
                button.hide()
            for rule in self._rules:
                rule.hide()

            self._rule = False

    def update_rule_opacity(self, opacity, absolute = False):
        """set rule opacity"""

    def add_rule_group(self):
        pass

    def remove_rule_group(self, index):
        pass

    def reset_rules(self):
        pass
