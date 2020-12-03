import utils.functions as utils


class Player:
    def __init__(self, id, grids=((1, 1), (1, 2), (1, 3))):
        self.id = id
        self.grids = list(grids)
        self.direction = self.get_default_direction()
        self.alive = True
        self.energy = 0

    def head(self):
        return None if len(self.grids) == 0 else self.grids[-1]

    def get_default_direction(self):
        if len(self.grids) == 1:
            return None
        direction = utils.add(self.head(), utils.negative(self.grids[-2]))
        if direction[0] ** 2 + direction[1] ** 2 == 1:
            return direction

    def get_target(self):
        return utils.add(self.head(), self.direction)

    def set_direction(self, direction):
        if direction[0] ** 2 + direction[1] ** 2 != 1:
            return [None]
        default_direction = self.get_default_direction()
        # length is 1 or direction is not BACK
        if default_direction is None or utils.add(direction, default_direction) != (0, 0):
            self.direction = tuple(direction)
        return [None]

    def move(self):
        if self.energy > 0:
            self.energy -= 1
        else:
            self.grids.pop(0)
        self.grids.append(self.get_target())

    def get_status(self):
        return {
            'grids': self.grids
        }
