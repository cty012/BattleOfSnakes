import json
import socket
import threading

import back.sprites.modules.map as m
import back.sprites.modules.player as p
import utils.colors as cl
from utils.parser import Parser


class Game:
    def __init__(self, args, mode, id, client):
        self.args = args
        self.mode = mode  # {'num-players', 'size', 'threshold', 'max-apples'}
        self.id = id
        self.client = client

        # map and players
        self.map = m.Map(
            self.args, self.args.get_pos(1, 1), dim=self.mode['size'],
            max_apples=self.mode['max-apples'], align=(1, 1))
        player_colors = cl.get_player_colors()
        init_grids = [
            [(1, i) for i in range(1, 4)],
            [(self.mode['size'][0] - 2, self.mode['size'][1] - i - 1) for i in range(1, 4)],
            [(self.mode['size'][0] - i - 1, 1) for i in range(1, 4)],
            [(i, self.mode['size'][1] - 2) for i in range(1, 4)]
        ]
        self.players = [p.Player(self.args, i, player_colors[i], init_grids[self.id]) for i in range(self.mode['num-players'])]
        self.map.focus_board(self.players[self.id].head())
        print(self.players[self.id].head())

        # thread
        self.send(json.dumps({'tag': 'start-game'}))
        threading.Thread(target=self.receive, name='client-recv', daemon=True).start()

    def process_events(self, events):
        # move the map
        self.map.process_events(events)

        # send the player commands to the server
        if self.players[self.id].alive:
            command = self.players[self.id].process_events(events)
            if command[0] == 'move':
                direction = command[1]
                if direction[0] ** 2 + direction[1] ** 2 == 1:
                    self.send(json.dumps({'tag': 'command', 'command': ['move', direction]}))
        return [None]

    def survivors(self):
        return [player for player in self.players if player.alive]

    def send(self, msg):
        msg_b = bytes(msg, encoding='utf-8')
        self.client.send(bytes(f'{len(msg_b):10}', encoding='utf-8') + msg_b)

    def receive(self):
        parser = Parser()
        end = False
        while not end:
            try:
                msg_strs = parser.parse(self.client.recv(1 << 20))
            except socket.timeout:
                continue
            except json.decoder.JSONDecodeError:
                print('\tJSON Decode Error!')
                continue
            # deal with msg
            for msg_str in msg_strs:
                msg = json.loads(msg_str)
                if msg['tag'] == 'status':
                    self.set_status(msg['status'])
                elif msg['tag'] == 'end-game':
                    end = True
        print(f'THREAD ENDS: player[{self.id}].sprites.game.receive()')

    def set_status(self, status):
        if 'map' in status:
            self.map.set_status(status['map'])
        if 'players' in status:
            for player in self.players:
                if str(player.id) in status['players']:
                    player.set_status(status['players'][str(player.id)])
                else:
                    player.alive = False

    def show(self, ui):
        self.map.show(ui)
        for player in self.survivors():
            self.map.show_player(ui, player)
