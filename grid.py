import pyglet as pgl


class Tile:
    def __init__(self, x, y, colour_ords, batch, scale=20, group=None, show = False):
        self._x, self._y, self._scale = x, y, scale
        self._activated = False
        self._colour_orders = colour_ords
        self._col_ind = 0

        self._batch = batch
        self._group = group
        self._culled = True

        self._tile = None
        self._highlight = None

        self.show(force=show)

    def update(self):
        """shift colour / direction to next element, return direction"""
        direction = self._colour_orders[self._col_ind]["dir"]

        self._col_ind += 1
        self._col_ind %= len(self._colour_orders)

        self._activated = True
        self.show()

        self._set_colour(self._colour_orders[self._col_ind]["col"])

        return direction

    def _set_colour(self, colour):
        """set tile colour"""
        if not self._culled:
            self._tile.colors = colour * 4

    def _update_tile(self):
        """update tile graphic"""
        if not self._culled:
            x, y, scale = self._x, self._y, self._scale

            border = scale / 20
            if border < 0.6:
                border = 0

            self._tile.vertices = [x + border, y + border, x + scale - border, y + border,
                                   x + scale - border, y + scale - border, x + border, y + scale - border]

            if self._activated:
                self._set_colour(self._colour_orders[self._col_ind]["col"])

            if self._highlight is not None:
                self._highlight.vertices = [x, y, x + scale, y, x + scale, y + scale, x, y + scale]

    def set_pos(self, x, y):
        """set position of graphic"""
        self._x = x
        self._y = y

        self._update_tile()

    def move(self, x, y, absolute=False):
        """move tile graphic"""
        if absolute:
            self._x = x
            self._y = y
        else:
            self._x += x
            self._y += y

        self._update_tile()

    def scale(self, dscale):
        """increase / decrease scale of graphic"""
        self._scale += dscale

        self._update_tile()

    def get_dims(self):
        """return x, y, scale"""
        return self._x, self._y, self._scale

    def highlight(self, colour=(255, 255, 255), reset=False):
        """highlight / outline tile"""
        if not self._culled:
            colour = list(colour)
            colour.append(100)

            if reset:
                if self._highlight is not None:
                    self._highlight.delete()
                    self._highlight = None

            elif self._highlight is None:
                if self._group is not None:
                    group = pgl.graphics.OrderedGroup(self._group.order + 1)
                else:
                    group = None

                x, y, scale = self._x, self._y, self._scale
                self._highlight = self._batch.add(4, pgl.gl.GL_QUADS, group,
                                                  ("v2f", (x, y, x + scale, y, x + scale, y + scale,
                                                           x, y + scale)),
                                                  ("c4B", (colour * 4)))

            else:
                self._highlight.colors = colour * 4

    def cull(self):
        """remove tile graphic (for when outside screen)"""
        if not self._culled:
            self._tile.delete()
            self._tile = None

            if self._highlight is not None:
                self.highlight(reset=True)

            self._culled = True

    def show(self, force = False):
        """add tile graphic"""
        if self._culled and self._activated or force:

            self._tile = self._batch.add(4, pgl.gl.GL_QUADS, self._group, ("v2f", (0, 0, 0, 0, 0, 0, 0, 0)),
                                         ("c3B", ([128] * 12)))

            self._culled = False
            self._update_tile()


class Grid:
    def __init__(self, size, colour_ords, batch, window, scale=20):
        self._origin = [(window.width - (size[0] * scale)) // 2, (window.height - (size[1] * scale)) // 2]

        self._tiles = [
            [Tile((col * scale) + self._origin[0], (row * scale) + self._origin[1], colour_ords, batch, scale = scale,
                  group=pgl.graphics.OrderedGroup(0)) for col in
             range(size[0])] for row
            in range(size[1])]

        self._scale = scale
        self._size = [size[0] - 1, size[1] - 1]
        self._colour_ords = colour_ords
        self._window = window
        self._batch = batch

        self._view_range = {"min_x": 0, "max_x": 0, "min_y": 0, "max_y": 50}
        self._update_view_range()
        self._cull()

    def update(self, x, y):
        """update tile at x, y. return direction"""
        return self._tiles[y][x].update()

    def get_size(self):
        """tile grid size"""
        return self._size

    def move(self, dx, dy):
        """move origin, update tiles pos"""
        self._origin[0] += dx
        self._origin[1] += dy

        self._cull(self._update_view_range())

        for row in range(self._view_range["min_y"], self._view_range["max_y"] + 1):
            for col in range(self._view_range["min_x"], self._view_range["max_x"] + 1):
                try:
                    self._tiles[row][col].move(dx, dy)
                except IndexError:
                    pass

    def scale(self, screen_x, screen_y, dscale):
        """update scale of all tiles if within scale bounds"""
        # limit scale
        if 2 < self._scale + dscale < 100:
            self._scale += dscale

            # center scaling around tile (move origin)
            row, col = self.get_tile(screen_x, screen_y, get_ind=True)

            if row is not None:
                self._origin[0] = screen_x - (col * self._scale) - self._scale / 2
                self._origin[1] = screen_y - (row * self._scale) - self._scale / 2

            for row_ind, row in enumerate(self._tiles):
                for col_ind, tile in enumerate(row):
                    tile.scale(dscale)
                    tile.set_pos((col_ind * self._scale) + self._origin[0], (row_ind * self._scale) + self._origin[1])

        self._cull(self._update_view_range())

    def add_dim(self, side):
        """add 1 row / col to tile grid"""
        if side == 0:  # top
            self._size[1] += 1
            self._tiles.append([Tile((col * self._scale) + self._origin[0],
                                     (self._size[1] * self._scale) + self._origin[1], self._colour_ords, self._batch,
                                     scale=self._scale, group=pgl.graphics.OrderedGroup(0)) for col in
                                range(self._size[0] + 1)])

        elif side == 1:  # right
            self._size[0] += 1
            for row_ind, row in enumerate(self._tiles):
                row.append(Tile((self._size[0] * self._scale) + self._origin[0],
                                (row_ind * self._scale) + self._origin[1], self._colour_ords, self._batch,
                                scale=self._scale, group=pgl.graphics.OrderedGroup(0)))

        elif side == 2:  # bottom
            self._size[1] += 1
            self._origin[1] -= self._scale
            self._tiles.insert(0, ([Tile((col * self._scale) + self._origin[0],
                                         self._origin[1], self._colour_ords, self._batch, scale=self._scale,
                                         group=pgl.graphics.OrderedGroup(0)) for col in range(self._size[0] + 1)]))

        elif side == 3:  # left
            self._size[0] += 1
            self._origin[0] -= self._scale
            for row_ind, row in enumerate(self._tiles):
                row.insert(0, (Tile(self._origin[0], (row_ind * self._scale) + self._origin[1], self._colour_ords,
                                    self._batch, scale=self._scale, group=pgl.graphics.OrderedGroup(0))))

        self._cull(self._update_view_range(), force=True)

    def get_tile(self, x_pos, y_pos, get_ind=False, by_ind=False):
        """return tile that has screen position x, y"""
        if by_ind:
            return self._tiles[y_pos][x_pos]

        for row_ind, row in enumerate(self._tiles):
            for col_ind, tile in enumerate(row):
                x, y, scale = tile.get_dims()

                if x < x_pos < x + scale and y < y_pos < y + scale:
                    if get_ind:
                        return row_ind, col_ind

                    return tile

        if get_ind:
            return None, None
        return None

    def delete(self):
        for row in self._tiles:
            for tile in row:
                tile.cull()
                del tile

    def _update_view_range(self):
        """update rows, cols that are in view"""
        old_min_x = self._view_range["min_x"]
        old_max_x = self._view_range["max_x"]
        old_min_y = self._view_range["min_y"]
        old_max_y = self._view_range["max_y"]

        self._view_range["min_x"] = int((0 - self._origin[0]) // self._scale) - 1
        self._view_range["max_x"] = int((self._window.width - self._origin[0]) // self._scale) + 1
        self._view_range["min_y"] = int((0 - self._origin[1]) // self._scale) - 1
        self._view_range["max_y"] = int((self._window.height - self._origin[1]) // self._scale) + 1

        if self._view_range["min_x"] < 0: self._view_range["min_x"] = 0
        if self._view_range["max_x"] < 0: self._view_range["max_x"] = 0
        if self._view_range["min_y"] < 0: self._view_range["min_y"] = 0
        if self._view_range["max_y"] < 0: self._view_range["max_y"] = 0

        return old_min_x - self._view_range["min_x"], old_max_x - self._view_range["max_x"], \
            old_min_y - self._view_range["min_y"], old_max_y - self._view_range["max_y"]

    def _cull(self, deltas=None, force = False):
        """hide all tiles outside of view range"""
        min_x = self._view_range["min_x"]
        max_x = self._view_range["max_x"]
        min_y = self._view_range["min_y"]
        max_y = self._view_range["max_y"]

        if deltas is None:
            for row in range(len(self._tiles)):
                for col in range(len(self._tiles[row])):
                    if not min_x <= col <= max_x or not min_y <= row <= max_y:
                        self._tiles[row][col].cull()
                    else:
                        self._tiles[row][col].show()

        else:
            d_min_x, d_max_x, d_min_y, d_max_y = deltas

            if not d_min_x == d_max_x == d_min_y == d_max_y == 0 or force:

                for row in range(min(min_y, min_y - d_min_y) - 2, max(max_y, max_y - d_max_y) + 2):
                    for col in range(min(min_x, min_x - d_min_x) - 2, max(max_x, max_x - d_max_x) + 2):
                        try:
                            if min_x <= col <= max_x and min_y <= row <= max_y:
                                self._tiles[row][col].show()
                                self._tiles[row][col].move((col * self._scale) + self._origin[0],
                                                           (row * self._scale) + self._origin[1], absolute=True)
                            else:
                                self._tiles[row][col].cull()
                        except IndexError:
                            pass
