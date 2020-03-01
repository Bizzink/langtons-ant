import pyglet as pgl
import menu_button
from menu_button import Button, Slider
from random import randint
from colorsys import hsv_to_rgb


g = None
main_menu = None
rule_menu = None


class Globals:
    def __init__(self, window, batch, functions, rule_list):
        self.window = window
        self.batch = batch
        self.functions = functions
        self.rule_list = rule_list
        self.scale = window.width * 0.00013


def init(window, batch, functions, rule_list):
    global g, main_menu, rule_menu
    g = Globals(window, batch, functions, rule_list)
    menu_button.init(batch, window)
    group = pgl.graphics.OrderedGroup(1)
    main = Menu(int(window.width * 0.96), 0, int(window.width * 0.04), window.height, group)
    rule = RuleMenu(int(window.width * 0.845), 0, int(window.width * 0.112), window.height, group)

    # main setup
    x = main.x + main.w // 2
    w = main.w
    h = window.height

    main.add_button(Button(["play.png", "pause.png"], [functions["pause"], rule.hide], g.scale, x=x, y=h * 0.96))
    main.add_button(Button(["restart.png"], [functions["reset"]], g.scale, x=x, y=h * 0.885))
    main.add_button(Button(["fast.png"], [], g.scale, clickable=False, x=x, y=h * 0.78))
    main.add_button(Button(["slow.png"], [], g.scale, clickable=False, x=x, y=h * 0.23))
    main.add_button(Button(["counter_on.png", "counter_off.png"], [functions["toggle_counter"]], g.scale, x=x, y=h * 0.12))
    main.add_button(Button(["settings.png"], [rule.toggle, functions["pause"]], g.scale, x=x, y=h * 0.05))

    main.add_slider(Slider((x, h * 0.52, h - w * 8, "vertical"), (1, 50, 2), [functions["set_speed"]], g.scale))

    main.add_primitive([5, h - w * 2.3, 5, h - w * 2.3 + 2, w - 5, h - w * 2.3 + 2, w - 5, h - w * 2.3], [76, 76, 76])
    main.add_primitive([5, w * 2.3,  5, w * 2.3 + 2, w - 5, w * 2.3 + 2, w - 5, w * 2.3], [76, 76, 76])
    main.add_primitive([w / 2 - 2, w * 4, w / 2 - 2, h - w * 4, w / 2 + 2, h - w * 4, w / 2 + 2, w * 4], [76, 76, 76])

    # rule setup
    x = rule.x + rule.w / 2

    rule.add_button(Button(["reset.png"], [rule.reset_rules], g.scale, x=x, y=h * 0.03))
    rule.add_button(Button(["add.png"], [rule.add_rule], g.scale * 0.7, x=x, y=h * 0.05))
    rule.add_rule(permanent=True, colour = [255, 255, 255], arrow = False)
    rule.add_rule(permanent=True, flipped=True, colour = [255, 0, 0])

    main_menu = main
    rule_menu = rule

    return main, rule


class Menu:
    def __init__(self, x, y, w, h, group, bg = 51):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self._visible = 0
        self._opacity = 255
        self._group = group
        self._buttons = []
        self._sliders = []
        self._primitives = []
        self._rules = []

        self.add_primitive([0, 0, 0, h, w, h, w, 0], [bg, bg, bg])

    def click(self, x, y):
        """pass click event to all buttons"""
        if self._visible:
            for button in self._buttons: button.click(x, y)
            for rule in self._rules: rule.click(x, y)

    def mouse_over(self, x, y):
        """pass mouse over event to all buttons if mouse is in menu region"""
        if self._visible:
            min_x = self.x
            max_x = self.x + self.w
            min_y = self.y
            max_y = self.y + self.h

            if min_x < x < max_x and min_y < y < max_y:
                for button in self._buttons: button.mouse_over(x, y)
                for rule in self._rules: rule.mouse_over(x, y)
                for slider in self._sliders: slider.mouse_over(x, y)
                return True

    def mouse_drag(self, dx, dy):
        """pass drag event to all sliders"""
        for slider in self._sliders:
            slider.drag(dx, dy)

    def toggle(self):
        """toggle show / hide"""
        if self._visible: self.hide()
        else: self.show()

    def show(self):
        """show all elements"""
        for button in self._buttons: button.visible = True
        for slider in self._sliders: slider.visible = True
        for rule in self._rules: rule.show()
        self._visible = 1
        self.update_opacity()

    def hide(self):
        """hide all elements"""
        for button in self._buttons: button.visible = False
        for slider in self._sliders: slider.visible = False
        for rule in self._rules: rule.hide()
        self._visible = 0
        self.update_opacity()

    def add_button(self, button):
        """add button to buttons"""
        self._buttons.append(button)

    def add_slider(self, slider):
        """add slider to sliders"""
        self._sliders.append(slider)

    def add_primitive(self, points: list, colour: list):
        """add primitive to primitives, co-ordinates relative to self x, y"""
        colour = colour.copy()
        colour.append(self._opacity * self._visible)

        for i in range(0, len(points), 2):
            points[i] = int(points[i] + self.x)
            points[i + 1] = int(points[i + 1] + self.y)

        self._primitives.append(g.batch.add(4, pgl.gl.GL_QUADS, self._group, ("v2i", points), ("c4B", (colour * 4))))

    def update_opacity(self, opacity = None, absolute = False):
        """update primitives opacity"""
        if opacity is not None:
            if absolute:
                self._opacity = opacity
            else:
                self._opacity += opacity

            for button in self._buttons: button.opacity = self._opacity
            for slider in self._sliders: slider.opacity = self._opacity

        for primitive in self._primitives:
            colour = primitive.colors[:3]
            colour.append(self._opacity * self._visible)
            primitive.colors = colour * 4


class RuleMenu(Menu):
    def __init__(self, x, y, w, h, group):
        super().__init__(x, y, w, h, group)

    def add_rule(self, permanent=False, flipped=False, colour=None, arrow=True):
        """add new rule at next index"""
        y = self.h * (1 - len(self._rules) * 0.075) - self.h * 0.06
        self._rules.append(Rule(self.x + self.w / 2, y, self.w * 0.9, pgl.graphics.OrderedGroup(self._group.order + 1),
                                flipped=flipped, permanent=permanent, colour=colour, arrow=arrow))

        if self._visible:
            self._rules[-1].show()

        self.rule_update()

    def rule_update(self):
        """update add button pos, remove deleted rules"""
        for rule in self._rules:
            if rule.removed:
                self._rules.remove(rule)

        if len(self._rules) == 12:
            self._buttons[1].clickable = False
            self._buttons[1].color = [128, 128, 128]
        else:
            self._buttons[1].clickable = True
            self._buttons[1].color = [255, 255, 255]

        self._buttons[1].y = self.h * (1 - len(self._rules) * 0.075) - self.h * 0.02

    def reset_rules(self):
        """remove all rule apart from first 2"""
        for rule in self._rules[2:]:
            rule.delete()


class Rule(Menu):
    def __init__(self, x, y, w, group, flipped = False, permanent = False, colour = None, arrow = True):
        super().__init__(int(x - w / 2), int(y), int(w), int(w // 3.5), group, bg = 37)

        if colour is None:
            hue = randint(0, 256) / 256
            colour = [int(val * 255) for val in hsv_to_rgb(hue, 0.8, 0.9)]

        g.rule_list.append({"colour": colour, "direction": "left"})

        self._rule = g.rule_list[-1]
        self.removed = False

        y = self.y + self.h / 2
        group = pgl.graphics.OrderedGroup(group.order + 1)

        self.add_button(Button(["colour.png"], [], g.scale * 0.7, x=x - w * 0.35, y=y, group=group))
        self._buttons[0].color = self._rule["colour"]
        self.add_button(Button(["arrow.png"], [self.switch_direction], g.scale * 0.7, x=x - w * 0.07, y=y, group=group))
        self.add_button(Button(["remove.png"], [self.delete], g.scale * 0.7, x=x + w * 0.3, y=y, group=group))
        self.add_primitive(
            [w * 0.61, self.h * 0.1, w * 0.61, self.h * 0.9, w * 0.61 + 3, self.h * 0.9, w * 0.61 + 3, self.h * 0.1],
            [64, 64, 64])

        if permanent:
            self._buttons[2].clickable = False
            self._buttons[2].color = [128, 128, 128]

        if flipped: self.switch_direction()

        if arrow: self.add_button(Button(["next.png"], [], g.scale, x=x, y=y + self.h * 0.75, group=group))

    def switch_direction(self):
        """switch turn direction in rule, button"""
        if self._rule["direction"] == "left":
            self._rule["direction"] = "right"
            self._buttons[1].scale_x = -1
        else:
            self._rule["direction"] = "left"
            self._buttons[1].scale_x = 1

    def delete(self):
        """delete self and all elements and rule at index"""
        self.removed = True
        for button in self._buttons: button.delete()
        for primitive in self._primitives: primitive.delete()
        g.rule_list.remove(self._rule)
        rule_menu.rule_update()
