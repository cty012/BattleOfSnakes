import json
from random import randint
import socket
from threading import Thread

import back.sprites.component as c
import utils.colors as cl
import utils.fonts as f


class Scene:
    def __init__(self, args):
        # arguments
        self.args = args
        self.mode = {
            'room-id': hex(randint(0, 16 ** 8 - 1)),
            'num-players': None,
            'size': (30, 30),
            'threshold': 1,
            'max-apples': 3
        }

        # gui
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))
        self.buttons = {
            'play': c.Button(
                (self.args.size[0] // 2 - 300, 620), (300, 60), 'start game',
                font=f.tnr(23), save='tnr-23', align=(1, 1), background=(210, 210, 210)
            ),
            'back': c.Button(
                (self.args.size[0] // 2 + 300, 620), (300, 60), 'close room',
                font=f.tnr(23), save='tnr-23', align=(1, 1), background=(210, 210, 210)
            ),
        }

    def process_events(self, events):
        if events['mouse-left'] == 'down':
            for name in self.buttons:
                if self.buttons[name].in_range(events['mouse-pos']):
                    return self.execute(name)
        if 'return' in events['key-down']:
            return self.execute('play')
        return [None]

    def add_clients(self, status):
        def func():
            print('\nSERVER START accepting...')
            while status['running'] and len(self.clients) < 7:
                try:
                    client_socket, address = self.server.accept()
                    self.clients.append({'ip': address[0], 'port': address[1], 'socket': client_socket})
                    print(f'\tSERVER establish connection to {address}')
                    ip_list = [self.ip] + [client['ip'] for client in self.clients]
                    for id in range(len(self.clients)):
                        self.send(json.dumps({'tag': 'info', 'id': id + 1, 'ip-list': ip_list}), id + 1)
                except socket.timeout:
                    pass
            print('SERVER END accepting...')
        return func

    def execute(self, name):
        if name == 'play':
            self.status['running'] = False
            # send info to clients
            for i in range(len(self.clients)):
                self.send(json.dumps({'tag': 'play'}), i + 1)
            return ['game', {
                'id': 0, 'num': len(self.clients) + 1, 'socket': self.server,
                'clients': self.clients
            }]
        elif name == 'back':
            self.send_all(json.dumps({'tag': 'close'}))
            self.status['running'] = False
            self.server.close()
            return ['menu']
        return [None]

    def send(self, msg, id):
        msg_b = bytes(msg, encoding='utf-8')
        self.clients[id - 1]['socket'].send(bytes(f'{len(msg_b):10}', encoding='utf-8'))
        self.clients[id - 1]['socket'].send(msg_b)

    def send_all(self, msg):
        msg_b = bytes(msg, encoding='utf-8')
        for id in range(len(self.clients)):
            self.clients[id]['socket'].send(bytes(f'{len(msg_b):10}', encoding='utf-8'))
            self.clients[id]['socket'].send(msg_b)

    def show(self, ui):
        self.background.show(ui)
        ui.show_text((self.args.size[0] // 2, 100), f'IP: {self.ip}', f.cambria(60), color=(0, 0, 128), align=(1, 1))

        # show ip title
        ui.show_text((self.args.size[0] // 2, 180), 'client ip', f.tnr(30), color=(128, 0, 0), align=(1, 1))
        ui.show_div((self.args.size[0] // 2, 210), (800, 352), color=(191, 220, 187), align=(1, 0))

        # show ip lists
        ip_list = [self.ip] + [client['ip'] for client in self.clients]
        for i in range(8):
            row, col = i % 4, i // 4
            pos = (self.args.size[0] // 2 - 200 + 400 * col, 254 + 84 * row)
            color = self.player_colors[i]
            if i == 0:
                ui.show_div(pos, (368, 56), color=color, align=(1, 1))
                ui.show_div((pos[0], pos[1] + 28), (368, 12), color=cl.multiply(color, 0.8), align=(1, 0))
                ui.show_text(
                    pos, ip_list[i], f.tnr_bold(25),
                    color=cl.white, save='tnr-bold-25-white', align=(1, 1))
            elif i < len(ip_list):
                ui.show_div(pos, (368, 56), color=cl.white, align=(1, 1))
                ui.show_div((pos[0], pos[1] + 28), (368, 12), color=color, align=(1, 0))
                ui.show_text(
                    pos, ip_list[i], f.tnr_bold(25),
                    save='tnr-bold-25', align=(1, 1))
            else:
                ui.show_div(pos, (368, 56), color=cl.white, align=(1, 1))
                ui.show_div((pos[0], pos[1] + 28), (368, 12), color=cl.white, align=(1, 0))

        # show buttons
        for name in self.buttons:
            self.buttons[name].show(ui)
