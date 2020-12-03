import json

import back.sprites.modules.map as m
import back.sprites.modules.player as p
import utils.stopwatch as sw
import utils.colors as cl


class Game:
    def __init__(self, args, mode, id, threshold=1):
        self.args = args
        self.mode = mode  # {'num-players', 'size', 'threshold', 'max-apples'}
        self.id = id

        # map and players
        self.map = m.Map(
            self.args, self.args.get_pos(1, 1), dim=self.mode['size'],
            max_apples=self.mode['max-apples'], align=(1, 1))
        player_colors = cl.get_player_colors()
        self.players = [p.Player(self.args, i, player_colors[i]) for i in range(self.mode['num-players'])]
        self.map.focus_board(self.players[self.id].head())

        # timer
        self.timer = sw.Stopwatch()
        self.timer.start()

    def process_events(self, events):
        # move the map
        self.map.process_events(events)

        # send the player commands to the server
        if self.players[self.id].alive:
            direction = self.players[self.id].process_events(events)
            if direction[0] ** 2 + direction[1] ** 2 == 1:
                self.send(json.dumps({'id': self.id, 'command': ['move', direction]}))
        return [None]

    def survivors(self):
        return [player for player in self.players if player.alive]

    def send(self, msg):
        # TODO: send individual msg to server
        pass

    def receive(self):
        while True:
            # TODO: receive the json string
            received_string = '{"tag":"status","status":{}}'
            msg = json.loads(received_string)
            if msg['tag'] == 'status':
                self.set_status(msg['status'])

    def set_status(self, status):
        if 'map' in status:
            self.map.set_status(status['map'])
        if 'players' in status:
            for player in self.players:
                if player.id in status['players']:
                    player.set_status(status['players'][player.id])
                else:
                    player.alive = False

    def show(self, ui):
        self.map.show(ui)
        for player in self.survivors():
            self.map.show_player(ui, player)
