import pyglet as pgl


class Tile:
    def __init__(self, x, y, colour_ords, batch, scale=20, group=None):
        self._x, self._y, self._scale = x, y, scale
        self._activated = False
        self._colour_orders = colour_ords
        self._col_ind = 0

        self._batch = batch
        self._group = group

        border = scale / 10
        self._tile = self._batch.add(4, pgl.gl.GL_QUADS, self._group,
                                     ("v2f", (x + border, y + border, x + scale - border, y + border,
                                              x + scale - border, y + scale - border, x + border, y + scale - border)),
                                     ("c3B", ([128] * 12)))

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
        x, y, scale = self._x, self._y, self._scale
        border = scale / 10

        self._tile.vertices = [x + border, y + border, x + scale - border, y + border,
                               x + scale - border, y + scale - border, x + border, y + scale - border]

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


class Grid:
    def __init__(self, origin, size, colour_ords, batch, scale=20, group=None):
        self._tiles = [
            [Tile((col * scale) + origin[0], (row * scale) + origin[1], colour_ords, batch, scale, group) for col in range(size[0])] for row
            in range(size[1])]
        self._origin = origin
        self._scale = scale

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

    def scale(self, dscale):
        """update scale of all tiles if within scale bounds"""
        if 10 < self._scale + dscale < 40:
            self._scale += dscale

            for row_num, row in enumerate(self._tiles):
                for col, tile in enumerate(row):
                    tile.scale(dscale)
                    tile.set_pos((col * self._scale) + self._origin[0], (row_num * self._scale) + self._origin[1])


