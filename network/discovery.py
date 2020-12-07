import logging
import socket
import threading
import time


class DiscoveryMirror:
    def __init__(self, mgroup, port, key, info, *, timeout=1.0, exc_meltdown=(3, 2.0), autostart=False):
        """
        :param mgroup: Multicast group ip (receive all messages sent to this ip)
        :type mgroup: str
        :param port: A list of available ports that will be used
        :type port: Sequence[int]
        :param key: Identify the application
        :type key: bytes
        :param info: Information sent to the client after connection is established
        :type info: bytes
        :param timeout: Timeout in seconds for receiving
        :type timeout: float
        :param exc_meltdown: Meltdown for retrying after exceptions
        :type exc_meltdown: Tuple[int, Union[int, float]]
        :param autostart: Whether the server will automatically start listening for requests
        :type autostart: bool
        """
        self.multicast_group = mgroup
        self.port = port
        self.key = key
        self.info = info
        self.timeout = timeout
        self.exc_meltdown = exc_meltdown

        self.sock = None
        self.status = 0

        self.thread = None
        self.running = False
        self.stopping = False
        self.reflecting = False

        if autostart:
            self.start()

    def bind_sock(self):
        for p in self.port:
            try:
                self.sock.bind(('', p))
                return
            except:
                pass
        raise RuntimeError('No available port')

    def reconnect(self):
        mgroup = self.multicast_group
        ip = '0.0.0.0'
        port = self.port

        membership = socket.inet_aton(mgroup) + socket.inet_aton(ip)

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.settimeout(self.timeout)
            self.bind_sock()
        except Exception as e:
            self.sock = None
            logging.warning(f"DiscoveryMirror @ {(mgroup, ip, port)} reconnect met unexpected exception", exc_info=e)
            return 1

        return 0

    def disconnect(self):
        try:
            self.sock.close()
        except:
            pass
        self.sock = None
        return 0

    def threadfunc(self):
        self.reflecting = True
        self.status = 0
        if self.reconnect():
            self.status = 1
            self.reflecting = False
            return
        sock = self.sock

        em_cnt = self.exc_meltdown[0]
        while self.running:
            try:
                msg, peer = sock.recvfrom(len(self.key))
                if msg == self.key:
                    sock.sendto(self.info, peer)
                em_cnt = self.exc_meltdown[0]
            except socket.timeout as e:
                continue
            except Exception as e:
                logging.warning(f"DiscoveryMirror @ {(self.multicast_group, self.port)} threadfunc met unexpected exception", exc_info=e)
                em_cnt -= 1
                if em_cnt == 0:
                    em_cnt = 1
                    time.sleep(self.exc_meltdown[1])

        self.reflecting = False

    def start(self):
        if self.running or self.stopping:
            return 1
        self.running = True
        self.thread = threading.Thread(target=self.threadfunc, daemon=True)
        self.thread.start()
        return 0

    def _cleanstop(self, cb=None):
        self.running = False
        self.thread.join()
        self.thread = None
        self.disconnect()
        if cb is not None:
            cb(0, self)
        self.stopping = False

    def stop(self, cb=None) -> int:
        if self.stopping or not self.running:
            return 1
        self.stopping = True
        cleanstop_thread = threading.Thread(target=self._cleanstop, args=(cb,))
        cleanstop_thread.start()
        return 0

    def __del__(self):
        self.stop()


class DiscoveryBeacon:
    def __init__(self, mgroup, port, key, *, timeout=1.0, exc_meltdown=(3, 2.0), autostart=False):
        """
        :param mgroup: Multicast group ip (receive all messages sent to this ip)
        :type mgroup: str
        :param port: A list of available ports that will be used
        :type port: Sequence[int]
        :param key: Identify the application
        :type key: bytes
        :param timeout: Timeout in seconds for receiving
        :type timeout: float
        :param exc_meltdown: Meltdown for retrying after exceptions
        :type exc_meltdown: Tuple[int, Union[int, float]]
        :param autostart: Whether the client will automatically start sending requests
        :type autostart: bool
        """
        self.multicast_group = mgroup
        self.port = port
        self.key = key
        self.timeout = timeout
        self.exc_meltdown = exc_meltdown

        self.sock = None
        self.status = 0
        self.responses = {}

        self.thread = None
        self.running = False
        self.stopping = False
        self.waiting = False

        if autostart:
            self.start()

    def _ping(self):
        for p in self.port:
            self.sock.sendto(self.key, (self.multicast_group, p))

    def ping(self, clear=False):
        if clear:
            self.responses = {}
        fail = 0
        for p in self.port:
            try:
                self.sock.sendto(self.key, (self.multicast_group, p))
            except:
                fail += 1
        return fail

    def reconnect(self, ping=True) -> int:
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.settimeout(self.timeout)
            if ping:
                self._ping()
        except Exception as e:
            self.sock = None
            logging.warning(f"DiscoveryBeacon -> {(self.multicast_group, self.port)} reconnect met unexpected exception", exc_info=e)
            return 1
        return 0

    def disconnect(self):
        try:
            self.sock.close()
        except:
            pass
        self.sock = None
        return 0

    def threadfunc(self):
        self.waiting = True
        self.status = 0
        if self.reconnect():
            self.status = 1
            self.waiting = False
            return
        sock = self.sock

        em_cnt = self.exc_meltdown[0]
        while self.running:
            try:
                msg, peer = sock.recvfrom(4096)
                self.responses[peer] = msg
                em_cnt = self.exc_meltdown[0]
            except socket.timeout as e:
                continue
            except Exception as e:
                logging.warning(f"DiscoveryBeacon -> {(self.multicast_group, self.port)} threadfunc met unexpected exception", exc_info=e)
                em_cnt -= 1
                if em_cnt == 0:
                    em_cnt = 1
                    time.sleep(self.exc_meltdown[1])

        self.waiting = False

    def start(self, clear=True):
        if self.running or self.stopping:
            return 1
        self.running = True
        if clear:
            self.responses = {}
        self.thread = threading.Thread(target=self.threadfunc, daemon=True)
        self.thread.start()
        return 0

    def _cleanstop(self, clear=False, cb=None):
        self.running = False
        self.thread.join()
        self.thread = None
        self.disconnect()
        if clear:
            self.responses = {}
        if cb is not None:
            cb(0, self)
        self.stopping = False

    def stop(self, clear=False, cb=None):
        if self.stopping or not self.running:
            return 1
        self.stopping = True
        cleanstop_thread = threading.Thread(target=self._cleanstop, args=(clear, cb))
        cleanstop_thread.start()
        return 0

    def __del__(self):
        self.stop(clear=True)
