import json
import socket

import back.game.server as s
import back.sprites.component as c
from network.discovery import DiscoveryBeacon
import utils.fonts as f
from utils.parser import Parser


class Scene:
    def __init__(self, args):
        self.args = args
        self.pos = (0, 0)
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))
        self.buttons = {
            'sing': c.Button(
                (self.args.size[0] // 2, 300), (600, 80), 'Single Player',
                font=f.tnr(25), align=(1, 1), background=(210, 210, 210)),
            'mult': c.Button(
                (self.args.size[0] // 2, 400), (600, 80), 'Multiplayer',
                font=f.tnr(25), align=(1, 1), background=(210, 210, 210)),
            'back': c.Button(
                (self.args.size[0] // 2, 500), (600, 80), 'Back',
                font=f.tnr(25), align=(1, 1), background=(210, 210, 210))
        }
        self.mode = None

    def process_events(self, events):
        if events['mouse-left'] == 'down':
            for name in self.buttons:
                if self.buttons[name].in_range(events['mouse-pos']):
                    return self.execute(name)
        return [None]

    def connect_to_server(self, ip, port):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client.settimeout(0.3)
        while True:
            try:
                client.connect((ip, port))
                break
            except socket.timeout:
                pass
        while True:
            try:
                self.mode = self.receive(client)  # TODO: receive mode
                return client
            except socket.timeout:
                pass

    def receive(self, client_socket):
        parser = Parser()
        while True:
            # receive and parse msg
            try:
                msg_strs = parser.parse(client_socket.recv(1 << 20))
            except socket.timeout:
                continue
            except json.decoder.JSONDecodeError:
                print('\tJSON Decode Error!')
                continue
            # deal with msg
            for msg_str in msg_strs:
                msg = json.loads(msg_str)
                if msg['tag'] == 'mode':
                    return msg['mode']

    def execute(self, name):
        if name == 'sing':
            # launch server
            room_name = socket.gethostname()
            server = s.Server(room_name, {
                'version': 'sing',
                'num-players': None,
                'size': (30, 30),
                'threshold': 0,
                'max-apples': 3
            })
            server.start()

            # connect to server
            client = self.connect_to_server('127.0.0.1', server.port)
            return ['game', self.mode, 0, client]
        elif name == 'mult':
            # launch server
            room_name = socket.gethostname()
            server = s.Server(room_name, {
                'version': 'mult',
                'num-players': None,
                'size': (30, 30),
                'threshold': 0,
                'max-apples': 3
            })
            server.start()

            # discover the server
            beacon = DiscoveryBeacon('224.0.3.101', list(range(5000, 5100)), b'battleofsnakes')
            beacon.start()
            while True:
                beacon.ping(True)
                for (ip, port), info_b in beacon.responses.items():
                    info = json.loads(info_b.decode('utf-8'))
                    if info['name'] == room_name:
                        beacon.stop(clear=True, cb=lambda a, b: print('BEACON ENDS: scene=mode'))
                        return ['room', room_name, (ip, info['port']), server]
        elif name == 'back':
            return ['menu']
        return [None]

    def show(self, ui):
        self.background.show(ui)
        ui.show_text((self.args.size[0] // 2, 150), "Select A Version", font=f.cambria(60), align=(1, 1))
        for name in self.buttons:
            self.buttons[name].show(ui)
