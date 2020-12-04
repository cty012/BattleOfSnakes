import json
import socket
import threading

from network import DiscoveryMirror


class Server:
    def __init__(self, mode, ports=tuple(range(5000, 5100)), from_app=False):
        self.mode = mode
        self.ports = ports
        self.from_app = from_app
        self.status = 'accepting'

        # server
        self.ip = '0.0.0.0'
        self.launch_server()
        self.mirror = DiscoveryMirror(
            '224.0.3.101', self.ports), b'battleofsnakes', bytes(json.dumps(self.mode), encoding='utf-8'))
        self.mirror.start()

    def launch_server(self):
        for port in self.ports:
            try:
                self.server.bind((self.ip, port))
                self.server.settimeout(1.1)
                self.server.listen()
                break
            except:
                pass
        else:
            raise RuntimeError('No available port')

        # clients
        self.clients = []  # {ip, port, client}
        self.status = {'running': True}
        self.player_colors = cl.get_player_colors()
        self.thread = threading.Thread(target=self.add_clients(self.status), name='add-clients', daemon=True)
        self.thread.start()

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        threading.Thread(target=self.main_loop, name='server', daemon=self.from_app)

    def main_loop(self):
        while self.status == 'accepting':
            if self.mode['version'] == 'sing':
                self.
            try:
                client_socket, address = self.server.accept()
                self.clients.append({'ip': address[0], 'port': address[1], 'socket': client_socket})
                print(f'\tSERVER establish connection to {address}')
                ip_list = [self.ip] + [client['ip'] for client in self.clients]
                for id in range(len(self.clients)):
                    self.send(json.dumps({'tag': 'info', 'id': id + 1, 'ip-list': ip_list}), id + 1)
            except socket.timeout:
                pass
        while self.status == 'game':
            pass
