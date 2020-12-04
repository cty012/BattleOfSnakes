import json
import socket
import threading

import back.game.game as g
from network.discovery import DiscoveryMirror
from utils.parser import Parser


class Server:
    def __init__(self, mode, ports=tuple(range(5000, 5100)), from_app=False):
        self.mode = mode  # {'version', 'num-players', 'size', 'threshold', 'max-apples'}
        self.ports = ports
        self.from_app = from_app
        self.status = 'accepting'

        # server
        self.ip = '0.0.0.0'
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.port = None
        self.launch_server()
        self.mirror = DiscoveryMirror(
            '224.0.3.101', self.ports, b'battleofsnakes', bytes(json.dumps(self.mode), encoding='utf-8'))
        self.mirror.start()

        # clients
        self.clients = []  # {ip, port, client}
        self.status = 'accepting'

        self.game = None

    def ip_list(self):
        return [c[0] for c in self.clients]

    def launch_server(self):
        for port in self.ports:
            try:
                self.server.bind((self.ip, port))
                self.server.settimeout(0.3)
                self.server.listen()
                self.port = port
                break
            except:
                pass
        else:
            raise RuntimeError('No available port')

    def start(self):
        threading.Thread(target=self.main_loop, name='server', daemon=self.from_app).start()

    def main_loop(self):
        while self.status == 'accepting':
            try:
                client_socket, address = self.server.accept()
                self.clients.append([address[0], client_socket])
                threading.Thread(
                    target=self.receive, args=(address[0], client_socket),
                    name='server-recv', daemon=True
                ).start()
                self.update_info()
                print(f'SERVER establish connection to {address[0]}')
            except socket.timeout:
                pass
            if self.mode['version'] == 'sing' and len(self.clients) == 1:
                break
        self.status = 'game'
        self.mode['num-players'] = len(self.clients)
        self.game = g.Game(self.mode, self.clients)
        self.send_all(json.dumps({'tag': 'mode', 'mode': self.mode}))
        while self.status == 'game':
            command = self.game.process()
            if command[0] == 'end':
                self.status = 'end'
        print('THREAD ENDS: server.main_loop')

    def update_info(self):
        for id in range(len(self.clients)):
            self.send(json.dumps({'tag': 'info', 'id': id, 'ip-list': self.ip_list()}), id)

    def receive(self, ip, client_socket):
        parser = Parser()
        while self.status == 'accepting' and ip in self.ip_list():
            # receive and parse msg
            try:
                msg_strs = parser.parse(client_socket.recv(1 << 20))
            except socket.timeout:
                continue
            except json.decoder.JSONDecodeError:
                print('JSON Decode Error!')
                continue
            # deal with msg
            for msg_str in msg_strs:
                msg = json.loads(msg_str)
                if msg['tag'] == 'quit':
                    self.clients.remove([ip, client_socket])
                    return
                elif msg['tag'] == 'start-game':
                    self.status = 'game'
                    break
        threading.Thread(
            target=self.game.receive, args=(self.ip_list().index(ip),), name='server', daemon=True).start()
        print(f'THREAD ENDS: server.receive(ip={ip})')

    def send(self, msg, id):
        msg_b = bytes(msg, encoding='utf-8')
        self.clients[id][1].send(bytes(f'{len(msg_b):10}', encoding='utf-8'))
        self.clients[id][1].send(msg_b)

    def send_all(self, msg):
        msg_b = bytes(msg, encoding='utf-8')
        for id in range(len(self.clients)):
            self.clients[id][1].send(bytes(f'{len(msg_b):10}', encoding='utf-8'))
            self.clients[id][1].send(msg_b)
