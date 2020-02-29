from menu_button import Button


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

        self._handle = Button(["slider.png"], [], scale, x=cx, y=cy)

        # pos = val / (max_val - min_val) * length
        # val = pos / length * (max_val - min_val)

        if orientation == "vertical":
            self._handle.y = cy - (length / 2) + default_val / (max_val - min_val) * length
        elif orientation == "horizontal":
            self._handle.x = cx - (length / 2) + default_val / (max_val - min_val) * length
            self._handle.rotate(90)
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
                self._handle.y = self._cy - (self._length / 2) + pos - self._handle.height / 2
            else:
                self._handle.x = self._cx - (self._length / 2) + pos - self._handle.width / 2

    def show(self):
        self._handle.visible = True
        self._hidden = False

    def hide(self):
        self._handle.visible = False
        self._hidden = True
