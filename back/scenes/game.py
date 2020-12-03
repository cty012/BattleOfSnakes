import back.sprites.component as c
import back.sprites.game as g


class Scene:
    def __init__(self, args, mode):
        self.args = args
        self.mode = mode
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))
        self.game = g.Game(self.args, 0, 0)

    def process_events(self, events):
        return self.execute(self.game.process_events(events))

    def execute(self, command):
        return [None]

    def show(self, ui):
        self.background.show(ui)
        self.game.show(ui)
