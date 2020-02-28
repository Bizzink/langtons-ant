import pyglet as pgl
from menu_button import Button
import menu_colour_pick

g = None


class Globals:
    def __init__(self, batch, rule_list, button_scale, group):
        self.batch = batch
        self.rule_list = rule_list
        self.button_scale = button_scale
        self.group = group


def init(batch, rule_list, button_scale, group, window):
    global g
    g = Globals(batch, rule_list, button_scale, group)

    menu_colour_pick.init(batch, window)


class Rule:
    def __init__(self, x, y, w, index, permanent=False, flipped=False):
        # x = center
        self._x = x
        # y = bottom
        self._y = y
        self._w = w * 0.9

        self._rule = g.rule_list[index]
        self._hidden = True
        self._opacity = 255
        self._primitives = None
        self._buttons = []

        # Buttons
        buttons = pgl.graphics.OrderedGroup(g.group.order + 1)
        w = w * 0.9

        self._buttons.append(Button(x - w * 0.35, y + w // 7, "colour.png", g.button_scale * 0.7, None, group=buttons))
        self._buttons[0].tint(self._rule["colour"])

        self._buttons.append(Button(x - w * 0.07, y + w // 7, "arrow.png", g.button_scale * 0.7, self._switch_direction,
                                    group=buttons))

        if permanent:
            self._buttons.append(Button(x + w * 0.3, y + w // 7, "remove.png", g.button_scale * 0.7, None,
                                        group=buttons))
            self._buttons[2].tint((128, 128, 128))
        else:
            self._buttons.append(Button(x + w * 0.3, y + w // 7, "remove.png", g.button_scale * 0.7, self.delete,
                                        group=buttons))

        if flipped:
            self._switch_direction()

    def show(self):
        """draw all elements"""
        if self._hidden:
            x, y, w, h = int(self._x - (self._w // 2)), int(self._y), int(self._w), int(self._w // 3.5)
            self._primitives = []

            div_group = pgl.graphics.OrderedGroup(g.group.order + 1)

            self._primitives.append(g.batch.add(4, pgl.gl.GL_QUADS, g.group,
                                                ("v2i", (x, y, x, y + h, x + w, y + h, x + w, y)),
                                                ("c4B", ([37, 37, 37, self._opacity] * 4))))

            self._primitives.append(g.batch.add(4, pgl.gl.GL_QUADS, div_group,
                                                ("v2i", (
                                                    x + int(w * 0.6), y + int(h * 0.1),
                                                    x + int(w * 0.6), y + int(h * 0.9),
                                                    x + int(w * 0.6) + 2, y + int(h * 0.9),
                                                    x + int(w * 0.6) + 2, y + int(h * 0.1))),
                                                ("c4B", ([64, 64, 64, self._opacity] * 4))))

            for button in self._buttons:
                button.show()

            self._hidden = False

    def hide(self):
        """hide all elements"""
        if not self._hidden:
            for primitive in self._primitives:
                primitive.delete()
                self._primitives = None

            for button in self._buttons:
                button.hide()

            self._hidden = True

    def click(self, x, y):
        """pass click event to buttons"""
        for button in self._buttons:
            button.click(x, y)

    def mouse_over(self, x, y):
        """pass mouse over event to buttons"""
        for button in self._buttons:
            button.mouse_over(x, y)

    def _switch_direction(self):
        """switch turn direction in rule, button"""
        if self._rule["direction"] == "left":
            self._rule["direction"] = "right"
            self._buttons[1].flip(True)
        else:
            self._rule["direction"] = "left"
            self._buttons[1].flip(False)

    def _update_colour(self, colour):
        pass

    def delete(self):
        pass

    def update_opacity(self, opacity, absolute=False):
        pass
