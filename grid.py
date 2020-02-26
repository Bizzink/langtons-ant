import time

import pyglet as pgl


class Tile:
    def __init__(self, x, y, colour_ords, batch, scale=20, group=None):
        self._x, self._y, self._scale = x, y, scale
        self._activated = False
        self._colour_orders = colour_ords
        self._col_ind = 0

        self._batch = batch
        self._group = group
        self._culled = False

        border = scale / 20
        self._tile = self._batch.add(4, pgl.gl.GL_QUADS, self._group,
                                     ("v2f", (x + border, y + border, x + scale - border, y + border,
                                              x + scale - border, y + scale - border, x + border, y + scale - border)),
                                     ("c3B", ([128] * 12)))
        self._highlight = None

    def update(self):
        """shift colour / direction to next element, return direction"""
        direction = self._colour_orders[self._col_ind]["dir"]

        self._col_ind += 1
        self._col_ind %= len(self._colour_orders)

        self._set_colour(self._colour_orders[self._col_ind]["col"])

        return direction

    def _set_colour(self, colour):
        """set tile colour"""
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

            if self._highlight is not None:
                self._highlight.vertices = [x, y, x + scale, y, x + scale, y + scale, x, y + scale]

    def set_pos(self, x, y):
        """set position of graphic"""
        self._x = x
        self._y = y

        self._update_tile()

    def move(self, dx, dy):
        """move tile graphic by dx, dy"""
        self._x += dx
        self._y += dy

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
                self._highlight = self._batch.add(4, pgl.gl.GL_QUADS, group, ("v2f", (x, y, x + scale, y, x + scale, y + scale,
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

    def show(self):
        """add tile graphic"""
        if self._culled:
            x, y, scale = self._x, self._y, self._scale

            border = scale / 20
            if border < 0.6:
                border = 0

            self._tile = self._batch.add(4, pgl.gl.GL_QUADS, self._group,
                                         ("v2f", (0, 0, 0, 0, 0, 0, 0, 0)),
                                         ("c3B", ([128] * 12)))

            self._update_tile()

            self._culled = False


class Grid:
    def __init__(self, origin, size, colour_ords, batch, window, scale=20, group=None):
        self._tiles = [
            [Tile((col * scale) + origin[0], (row * scale) + origin[1], colour_ords, batch, scale, group) for col in
             range(size[0])] for row
            in range(size[1])]
        self._origin = origin
        self._scale = scale
        self._window = window

        self._cull()

        self._cull_range = {"min_x": 0, "max_x": size[0], "min_y": 0, "max_y": size[1]}

    def update(self, x, y):
        """update tile at x, y. return direction"""
        return self._tiles[y][x].update()

    def move(self, dx, dy):
        """move origin, update tiles pos"""
        self._origin[0] += dx
        self._origin[1] += dy

        for row in self._tiles:
            for tile in row:
                tile.move(dx, dy)

        self._cull()

    def scale(self, screen_x, screen_y, dscale):
        """update scale of all tiles if within scale bounds"""
        # limit scale
        if 10 < self._scale + dscale < 100:
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

        self._cull()

    def get_tile(self, x_pos, y_pos, get_ind = False, by_ind = False):
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

    def remove_all_highlights(self):
        for row in self._tiles:
            for tile in row:
                tile.highlight(reset=True)

    def _cull(self):
        # TODO: get culled rows, cols


        for row in self._tiles:
            for tile in row:
                x, y, scale = tile.get_dims()

                if x + scale < 0 or x > self._window.width or y + scale < 0 or y > self._window.height:
                    tile.cull()

                else:
                    tile.show()
