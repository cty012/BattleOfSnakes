import back.sprites.modules.apple as a
import utils.functions as utils


class Block:
    def __init__(self, args, grid, size, inner_size):
        self.args = args
        self.grid = grid
        self.size = size
        self.inner_size = inner_size
        self.color = (224, 224, 224)
        self.inner_color = (210, 210, 210)

    def get_rect(self, *, pan=(0, 0)):
        pos = (self.grid[0] * self.size, self.grid[1] * self.size)
        return [
            [pos[0] + pan[0], pos[1] + pan[1]],
            [pos[0] + self.size + pan[0], pos[1] + self.size + pan[1]]
        ]

    def in_range(self, pos, *, pan=(0, 0)):
        rect = self.get_rect(pan=pan)
        return rect[0][0] < pos[0] < rect[1][0] and rect[0][1] < pos[1] < rect[1][1]

    def show(self, ui, *, pan=(0, 0)):
        ui.show_div(
            (self.grid[0] * self.size, self.grid[1] * self.size),
            (self.size, self.size), color=self.color, pan=pan)
        self.show_inner(ui, pan=pan)

    def show_inner(self, ui, *, color=None, pan=(0, 0)):
        diff = (self.size - self.inner_size + 1) // 2
        ui.show_div(
            (self.grid[0] * self.size + diff, self.grid[1] * self.size + diff),
            (self.inner_size, self.inner_size), color=self.inner_color if color is None else color, pan=pan)


class Map:
    def __init__(self, args, pos, *, dim=(30, 30), max_apples=3, align=(0, 0)):
        self.args = args
        self.dim = dim
        self.grid_size = 31
        self.grid_inner_size = 22
        self.apple_radius = 6
        self.pos = utils.top_left(pos, self.size(), align=align)
        self.pan = [0, 0]

        self.blocks = [[
                Block(self.args, (i, j), self.grid_size, self.grid_inner_size)
                for j in range(self.dim[1])
            ] for i in range(self.dim[0])
        ]
        self.apples = []
        self.max_apples = max_apples
        self.steve_jobs = a.SteveJobs(self.args, self.dim, self.grid_size, self.apple_radius, max_size=self.max_apples)

    def size(self, direction=None):
        size = self.dim[0] * self.grid_size, self.dim[1] * self.grid_size
        return size if direction is None else size[direction]

    def get_rect(self, *, pan=(0, 0)):
        pan = utils.add(self.pan, pan)
        return [
            [self.pos[0] + pan[0], self.pos[1] + pan[1]],
            [self.pos[0] + self.size(0) + pan[0], self.pos[1] + self.size(1) + pan[1]]
        ]

    def in_range(self, pos, *, pan=(0, 0)):
        rect = self.get_rect(pan=pan)
        return rect[0][0] < pos[0] < rect[1][0] and rect[0][1] < pos[1] < rect[1][1]

    def get(self, grid):
        return self.blocks[grid[0]][grid[1]]

    def process_events(self, events):
        direction = [0, 0]
        for key in events['key-pressed']:
            if key == 'w':
                direction[1] -= 1
            elif key == 'a':
                direction[0] -= 1
            elif key == 's':
                direction[1] += 1
            elif key == 'd':
                direction[0] += 1
        self.move_board(tuple(direction))
        return [None]

    def focus_board(self, grid):
        grid_pos = utils.add(self.get(grid).get_rect()[0], (self.grid_size // 2, grid[1] // 2))
        self.pan = list(utils.add(self.args.get_pos(1, 1), utils.negative(self.pos), utils.negative(grid_pos)))
        self.pan[0] = utils.min_max(self.pan[0], -self.size(0) // 2, self.size(0) // 2)
        self.pan[1] = utils.min_max(self.pan[1], -self.size(1) // 2, self.size(1) // 2)

    def move_board(self, direction, speed=11):
        self.pan[0] = utils.min_max(self.pan[0] - speed * direction[0], -self.size(0) // 2, self.size(0) // 2)
        self.pan[1] = utils.min_max(self.pan[1] - speed * direction[1], -self.size(1) // 2, self.size(1) // 2)

    def set_status(self, status):
        for apple in self.apples:
            self.steve_jobs.back(apple)
        for grid in status['apples']:
            self.apples.append(self.steve_jobs.get(grid))

    def show(self, ui, *, pan=(0, 0)):
        # show blocks
        for row in self.blocks:
            for block in row:
                block.show(ui, pan=utils.add(self.pos, self.pan, pan))

        # show grid
        [[x_min, y_min], [x_max, y_max]] = self.get_rect(pan=pan)
        step = self.grid_size
        for col in range(self.dim[0] + 1):
            ui.show_line((x_min + col * step, y_min), (x_min + col * step, y_max))
        for row in range(self.dim[1] + 1):
            ui.show_line((x_min, y_min + row * step), (x_max, y_min + row * step))

        # show apples
        for apple in self.apples:
            apple.show(ui, pan=utils.add(self.pos, self.pan, pan))

    def show_player(self, ui, player, *, pan=(0, 0)):
        for grid in player.grids:
            self.get(grid).show_inner(ui, color=player.color, pan=utils.add(self.pos, self.pan, pan))
