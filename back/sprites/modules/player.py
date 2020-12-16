import utils.functions as utils


class Player:
    def __init__(self, args, id, color, grids):
        self.args = args
        self.id = id
        self.color = color
        self.grids = list(grids)
        self.alive = True

    def head(self):
        return None if len(self.grids) == 0 else self.grids[-1]

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
        return ['move', direction]

    def set_status(self, status):
        self.alive = True
        self.grids = [tuple(grid) for grid in status['grids']]
