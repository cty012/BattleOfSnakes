import utils.functions as utils


class Player:
    def __init__(self, args, id, color, grids=((1, 1), (1, 2), (1, 3))):
        self.args = args
        self.id = id
        self.color = color
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

    def process_events(self, events):
        direction = [0, 0]
        for key in events['key-down']:
            if key == 'up':
                direction[1] -= 1
            elif key == 'down':
                direction[1] += 1
            elif key == 'left':
                direction[0] -= 1
            elif key == 'right':
                direction[0] += 1
        if direction[0] ** 2 + direction[1] ** 2 == 1:
            default_direction = self.get_default_direction()
            if default_direction is None or utils.add(direction, default_direction) != (0, 0):
                self.direction = tuple(direction)
        return [None]

    def move(self):
        if self.energy > 0:
            self.energy -= 1
        else:
            self.grids.pop(0)
        self.grids.append(self.get_target())
