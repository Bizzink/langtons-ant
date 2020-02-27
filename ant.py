class Ant:
    def __init__(self, row, col, grid):
        self._direction = 0
        self._row = row
        self._col = col
        self._grid = grid
        self._steps = 0

    def update(self):
        """update tile and move"""
        grid_size = self._grid.get_size()

        if self._row <= 0:
            self._grid.add_dim(2)
            self._row += 1

        elif self._row >= grid_size[1]:
            self._grid.add_dim(0)

        if self._col <= 0:
            self._grid.add_dim(3)
            self._col += 1

        elif self._col >= grid_size[0]:
            self._grid.add_dim(1)

        tile = self._grid.get_tile(self._col, self._row, by_ind = True)
        self._update_direction(tile.update())
        self._move()

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

        self._steps += 1

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

    def get_steps(self):
        """return step count"""
        return self._steps
