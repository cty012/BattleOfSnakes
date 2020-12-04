import json

import back.game.map as m
import back.game.player as p
from network.discovery import DiscoveryBeacon, DiscoveryMirror
import utils.stopwatch as sw


class Game:
    def __init__(self, mode, connect):
        self.mode = mode  # {'num-players', 'size', 'threshold', 'max-apples'}
        self.connect = connect
        self.mirror = DiscoveryMirror()

        self.map = m.Map(dim=self.mode['size'], max_apples=self.mode['max-apples'])
        self.players = [
            p.Player(i, grids=[(2 * i + 1, j) for j in range(1, 4)])
            for i in range(self.mode['num-players'])
        ]
        self.map.generate_apples(self.players)

        self.status = {'running': True, 'connect': {i: True for i in range(self.mode['num-players'])}}

        # timer
        self.timer = sw.Stopwatch()
        self.timer.start()

    def process(self):
        self.send_all(json.dumps(self.get_status(), separators=(',', ':')))

        # check if game has already ended
        if not self.status['running']:
            return [None]

        if self.timer.get_time() < 0.2:
            return [None]

        # reset timer
        self.timer.clear()
        self.timer.start()

        # check if game ends
        self.check_alive()
        if len(self.survivors()) <= self.mode['threshold']:
            print('Game ends')
            self.status['running'] = False
            return ['end']

        # move surviving players and eat apples
        for player in self.survivors():
            player.move()
            remove_list = []
            for apple in self.map.apples:
                if apple.grid in player.grids:
                    player.energy += 1
                    remove_list.append(apple)
            for apple in remove_list:
                self.map.apples.remove(apple)

        # refill apples
        self.map.generate_apples(self.survivors())

    def execute(self, player_id, command):
        if command[0] == 'move':
            if self.players[player_id].alive:
                self.players[player_id].set_direction(command[1])
        elif command[0] == 'quit':
            if self.players[player_id].alive:
                self.players[player_id].alive = False
                for grid in self.players[player_id].grids:
                    if grid not in self.map.apples:
                        self.map.apples.append(grid)
            self.status['connect'][player_id] = False

    def survivors(self):
        return [player for player in self.players if player.alive]

    def is_valid_grid(self, grid):
        if not self.map.in_range(grid):
            return False
        for player in self.survivors():
            if grid in player.grids[1:]:
                return False
        return True

    def check_alive(self):
        new_heads, losers = {}, []
        for player in self.survivors():
            target = player.get_target()
            if not self.is_valid_grid(target):
                losers.append(player)
                continue
            if target in new_heads:
                losers.append(player)
                if new_heads[target] not in losers:
                    losers.append(new_heads[target])
                continue
            new_heads[target] = player
        for loser in losers:
            loser.alive = False

    def get_status(self):
        return {
            'map': self.map.get_status(),
            'players': {player: player.get_status() for player in self.players if player.alive}
        }

    def send(self, msg, client_id):
        # TODO: send individual msg to client
        pass

    def send_all(self, msg):
        # TODO: send group msg to all clients
        pass

    def receive(self, player_id):
        def func():
            while True:
                received_string = '{"tag":"command","command":[null]}'
                msg = json.loads(received_string)
                if msg['tag'] == 'command':
                    self.execute(player_id, msg['command'])
        return func
