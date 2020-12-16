import json
import socket
import threading

import back.game.map as m
import back.game.player as p
import utils.functions as utils
import utils.stopwatch as sw
from utils.parser import Parser


class Game:
    def __init__(self, mode, clients):
        self.mode = mode  # {'version', 'num-players', 'size', 'threshold', 'max-apples'}
        self.clients = clients

        self.map = m.Map(dim=self.mode['size'], max_apples=self.mode['max-apples'])
        init_grids = utils.get_init_grids(self.mode['size'])
        self.players = [
            p.Player(i, grids=init_grids[i])
            for i in range(self.mode['num-players'])
        ]
        self.map.generate_apples(self.players)

        self.status = {'running': True, 'connect': {i: True for i in range(self.mode['num-players'])}}

        # receive
        for id in range(self.mode['num-players']):
            threading.Thread(target=self.receive, args=(id,), name=f'server-recv{id}', daemon=True).start()

        # timer
        self.timer = sw.Stopwatch()
        self.timer.start()
        self.send_all(json.dumps({'tag': 'status', 'status': self.get_status()}, separators=(',', ':')))

    def process(self):
        if self.timer.get_time() < 0.2:
            return [None]

        # check if game has already ended
        if not self.status['running']:
            return [None]

        # reset timer
        self.timer.clear()
        self.timer.start()

        # check if game ends
        self.check_alive()
        if len(self.survivors()) <= self.mode['threshold']:
            self.send_all(json.dumps({'tag': 'end-game'}))
            self.status['running'] = False
            return ['end']

        # move surviving players and eat apples
        for player in self.survivors():
            player.move()
            remove_list = []
            for apple in self.map.apples:
                if apple in player.grids:
                    player.energy += 1
                    remove_list.append(apple)
            for apple in remove_list:
                self.map.apples.remove(apple)

        # refill apples
        self.map.generate_apples(self.survivors())

        self.send_all(json.dumps({'tag': 'status', 'status': self.get_status()}, separators=(',', ':')))
        return [None]

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
            for grid in loser.grids:
                if grid not in self.map.apples:
                    self.map.apples.append(grid)

    def toggle_pause(self):
        if self.timer.is_running():
            self.timer.stop()
        else:
            self.timer.start()

    def get_status(self):
        return {
            'map': self.map.get_status(),
            'players': {i: player.get_status() for i, player in enumerate(self.players) if player.alive}
        }

    def send(self, msg, id):
        msg_b = bytes(msg, encoding='utf-8')
        self.clients[id][1].send(bytes(f'{len(msg_b):10}', encoding='utf-8') + msg_b)

    def send_all(self, msg):
        msg_b = bytes(msg, encoding='utf-8')
        for id in range(len(self.clients)):
            self.clients[id][1].send(bytes(f'{len(msg_b):10}', encoding='utf-8'))
            self.clients[id][1].send(msg_b)

    def receive(self, player_id):
        parser = Parser()
        while self.players[player_id].alive:
            # receive and parse msg
            try:
                msg_strs = parser.parse(self.clients[player_id][1].recv(1 << 20))
            except socket.timeout:
                continue
            except json.decoder.JSONDecodeError:
                print('\tJSON Decode Error!')
                continue
            # deal with msg
            for msg_str in msg_strs:
                msg = json.loads(msg_str)
                if msg['tag'] == 'command':
                    self.execute(player_id, msg['command'])
                elif msg['tag'] == 'pause':
                    if player_id == 0:
                        self.toggle_pause()
        print(f'THREAD ENDS: game.game.receive(player_id={player_id})')
