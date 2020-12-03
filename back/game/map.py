from itertools import product
from random import choices

import utils.functions as utils


class Map:
    def __init__(self, dim=(30, 30), max_apples=3):
        self.dim = dim
        self.apples = []
        self.max_apples = max_apples

    def in_range(self, grid):
        return 0 <= grid[0] < self.dim[0] and 0 <= grid[1] < self.dim[1]

    def get_empty(self, players, *, remove_apples=True):
        grids = list(product(range(self.dim[0]), range(self.dim[1])))
        for player in players:
            for grid in player.grids:
                if grid in grids:
                    grids.remove(grid)
        if remove_apples:
            for apple in self.apples:
                if apple in grids:
                    grids.remove(apple)
        return grids

    def generate_apples(self, players, num=None):
        # recalculate num
        if num is None:
            num = self.max_apples - len(self.apples)
        empty = self.get_empty(players)
        num = utils.min_max(num, 0, len(empty))
        if num == 0:
            return

        # generate apples
        new_apple_grids = choices(empty, k=num)
        for grid in new_apple_grids:
            self.apples.append(grid)

    def get_status(self):
        return {
            'apples': self.apples
        }
