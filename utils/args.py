class Args:
    def __init__(self, scale=1, path='.', save_path='.'):
        self.scale = scale
        self.size = (1280, 720)
        self.real_size = int(self.size[0] * scale), int(self.size[1] * scale)

        self.path = path
        self.save_path = save_path

    def get_pos(self, align_x, align_y):
        return (
            [0, self.size[0] // 2, self.size[0]][align_x],
            [0, self.size[1] // 2, self.size[1]][align_y]
        )
