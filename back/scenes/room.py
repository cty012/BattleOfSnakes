import json
import socket
from threading import Thread

import back.sprites.component as c
import utils.colors as cl
import utils.fonts as f


class Scene:
    def __init__(self, args, room_name, address, server=None):
        # arguments
        self.args = args
        self.mode = None
        self.room_name = room_name
        self.displayed_room_name = (self.room_name[:17] + '......') if len(self.room_name) > 20 else self.room_name
        self.server_ip = address[0]
        self.port = address[1]
        self.server = server

        # client
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client.settimeout(0.3)
        self.client.connect((self.server_ip, self.port))

        # receive from server
        print('CLIENT ENTER room...')
        self.status = 'wait'
        self.id = None
        self.ip_list = []
        self.thread = Thread(target=self.wait_info, name='wait-info')
        self.thread.start()

        # gui
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))
        if self.server is None:
            self.buttons = {
                'back': c.Button(
                    (self.args.size[0] // 2, 630), (600, 80), 'Exit Room', font=f.tnr(25),
                    save='tnr-25', align=(1, 1), background=(210, 210, 210)),
            }
        else:
            self.buttons = {
                'play': c.Button(
                    (self.args.size[0] // 2 - 300, 630), (300, 60), 'Play', font=f.tnr(25),
                    save='tnr-25', align=(1, 1), background=(210, 210, 210)),
                'back': c.Button(
                    (self.args.size[0] // 2 + 300, 630), (300, 60), 'Close Room', font=f.tnr(25),
                    save='tnr-25', align=(1, 1), background=(210, 210, 210)),
            }
        self.player_colors = cl.get_player_colors()

    def process_events(self, events):
        if self.status != 'wait':
            return self.execute(self.status)
        if events['mouse-left'] == 'down':
            for name in self.buttons:
                if self.buttons[name].in_range(events['mouse-pos']):
                    return self.execute(name)
        return [None]

    def send(self, msg):
        msg_b = bytes(msg, encoding='utf-8')
        self.client.send(bytes(f'{len(msg_b):10}', encoding='utf-8') + msg_b)

    def wait_info(self):
        while self.status == 'wait':
            try:
                length = int(json.loads(self.client.recv(10).decode('utf-8')))
                msg = json.loads(self.client.recv(length).decode('utf-8'))
                if msg['tag'] == 'mode':
                    self.status = 'game'
                    self.mode = msg['mode']
                    break
                elif msg['tag'] == 'close':
                    self.status = 'back'
                    break
                elif msg['tag'] == 'info':
                    self.id = msg['id']
                    self.ip_list = msg['ip-list']
            except socket.timeout:
                pass
            except OSError:
                break
        print("THREAD ENDS: room.wait_info")

    def execute(self, name):
        if name == 'play':
            self.send(json.dumps({'tag': 'start-game'}))
        if name == 'game':
            print('CLIENT ENTER game...')
            return ['game', self.mode, self.id, self.client]
        elif name == 'back':
            self.close()
            print('CLIENT EXIT room...')
            return ['menu']
        return [None]

    def close(self):
        self.client.close()
        if self.server is not None:
            self.server.close()

    def show(self, ui):
        self.background.show(ui)
        ui.show_text((self.args.size[0] // 2, 100), f'{self.displayed_room_name}', f.cambria(60), color=(0, 0, 128), align=(1, 1))

        # show ip title
        ui.show_text((self.args.size[0] // 2, 180), 'client ip', f.tnr(30), color=(128, 0, 0), align=(1, 1))
        ui.show_div((self.args.size[0] // 2, 210), (800, 352), color=(191, 220, 187), align=(1, 0))

        # show ip lists
        for i in range(4):
            row = i % 4
            pos = (self.args.size[0] // 2, 254 + 84 * row)
            color = self.player_colors[i]
            if i == self.id and i < len(self.ip_list):
                ui.show_div(pos, (368, 56), color=color, align=(1, 1))
                ui.show_div((pos[0], pos[1] + 28), (368, 12), color=cl.multiply(color, 0.8), align=(1, 0))
                ui.show_text(
                    pos, self.ip_list[i], f.tnr_bold(25),
                    color=cl.white, save='tnr-bold-25-white', align=(1, 1))
            elif i < len(self.ip_list):
                ui.show_div(pos, (368, 56), color=cl.white, align=(1, 1))
                ui.show_div((pos[0], pos[1] + 28), (368, 12), color=color, align=(1, 0))
                ui.show_text(
                    pos, self.ip_list[i], f.tnr_bold(25),
                    save='tnr-bold-25', align=(1, 1))
            else:
                ui.show_div(pos, (368, 56), color=cl.white, align=(1, 1))
                ui.show_div((pos[0], pos[1] + 28), (368, 12), color=cl.white, align=(1, 0))

        for name in self.buttons:
            self.buttons[name].show(ui)
