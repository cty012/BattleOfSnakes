import json

import back.sprites.component as c
import back.sprites.game as g
import back.sprites.menus.game_menu as gm


class Scene:
    def __init__(self, args, mode, id, client):
        self.args = args
        self.mode = mode  # {'num-players', 'size', 'threshold', 'max-apples'}
        self.id = id
        self.client = client
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))
        self.game = g.Game(self.args, self.mode, self.id, self.client)
        self.game_menu = gm.GameMenu(self.args, self.args.get_pos(1, 1), align=(1, 1))

    def process_events(self, events):
        if self.game_menu.active:
            return self.execute(self.game_menu.process_events(events))
        for key in events['key-down']:
            if key == 'escape':
                self.execute(['pause'])
        return self.execute(self.game.process_events(events))

    def execute(self, command):
        if command[0] == 'pause':
            self.game.send(json.dumps({'tag': 'pause'}))
            self.game_menu.active = not self.game_menu.active
        elif command[0] == 'close':
            return ['menu']
        return [None]

    def show(self, ui):
        self.background.show(ui)
        self.game.show(ui)
        if self.game_menu.active:
            self.game_menu.show(ui)
