import utils.functions as utils


class Apple:
    def __init__(self, args, grid, grid_size, radius, color=(255, 215, 0)):
        self.args = args
        self.grid = grid
        self.grid_size = grid_size
        self.radius = radius
        self.color = color

    def get_rect(self, *, pan=(0, 0)):
        pos = (self.grid[0] * self.grid_size, self.grid[1] * self.grid_size)
        return [
            [pos[0] + pan[0], pos[1] + pan[1]],
            [pos[0] + self.grid_size + pan[0], pos[1] + self.grid_size + pan[1]]
        ]

    def show(self, ui, *, pan=(0, 0)):
        ui.show_circle(
            utils.add(self.get_rect()[0], ((self.grid_size + 1) // 2, (self.grid_size + 1) // 2)),
            self.radius, color=self.color, pan=pan)


class SteveJobs:
    def __init__(self, args, dim, grid_size, radius, color=(255, 215, 0), max_size=None):
        self.args = args
        self.dim = dim
        self.grid_size = grid_size
        self.radius = radius
        self.color = color
        self.max_size = dim[0] * dim[1] if max_size is None else max_size
        self.pool = []
        self.produce(self.max_size)

    def produce(self, num=1):
        for _ in range(num):
            self.pool.append(
                Apple(self.args, None, self.grid_size, self.radius, self.color))

    def get(self, grid):
        if len(self.pool) == 0:
            self.produce()
        apple = self.pool.pop(0)
        apple.grid = tuple(grid[:])
        return apple

    def back(self, apple):
        apple.grid = None
        self.pool.append(apple)
