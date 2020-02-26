class Ant:
    def __init__(self, row, col, grid):
        self._direction = 0
        self._row = row
        self._col = col
        self._grid = grid

    def update(self):
        """update tile and move"""
        try:
            tile = self._grid.get_tile(self._col, self._row, by_ind = True)
            direction = tile.update()
        except IndexError:
            return False
        except AttributeError:
            return False

        self._update_direction(direction)
        self._move()

        return True

    def _move(self):
        """move one space in facing direction"""
        # up = 0
        if self._direction == 0:
            self._row += 1

        # right = 1
        elif self._direction == 1:
            self._col += 1

        # down = 2
        elif self._direction == 2:
            self._row -= 1

        # left = 3
        elif self._direction == 3:
            self._col -= 1

    def _update_direction(self, direction):
        """rotate direction to left or right"""
        direction = direction.lower()

        if direction == "left":
            self._direction -= 1

        elif direction == "right":
            self._direction += 1

        else:
            raise ValueError(f"Invalid direction ({direction})")

        self._direction %= 4

    def get_pos(self):
        """return row, col"""
        return self._row, self._col
