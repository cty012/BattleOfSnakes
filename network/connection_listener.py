from typing import *
import logging
import random
import socket
import time
import threading

from ..utils import *


ConnectionHandler = Callable[[socket.socket], int]


class ConnectionListener:
    def __init__(
            self,
            port: Sequence[int],
            handler: ConnectionHandler,
            *,
            autostart: Union[bool, int] = True,
            timeout: Optional[Number_t] = 1.0,
            exc_meltdown: Tuple[int, Number_t] = (3, 2.0)
            ) -> None:

        self.port = port
        self.handler = handler  # TODO maybe a default handler
        self.timeout = timeout
        self.exc_meltdown = exc_meltdown

        self.svr: socket.socket = None
        self.stopping = False
        self.running = False
        self.accepting = False
        self.accept_thread: threading.Thread = None

        if autostart:
            self.start()

    def bind_svr(self) -> None:
        for p in self.port:
            try:
                self.svr.bind(('', p))
                return
            except:
                pass
        raise RuntimeError('Ports all unavailable')

    def reconnect(self, *, forced: bool = False) -> int:
        if self.svr and not forced:
            return 0
        try:
            self.svr.close()
        except:
            pass
        try:
            self.svr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.svr.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.svr.settimeout(self.timeout)
            self.bind_svr()
            self.svr.listen()
        except Exception as e:
            logging.warning('Unable to establish server', exc_info=e)
            self.svr = None
            return 1
        return 0

    def accept_loop(self) -> None:
        self.accepting = True
        em_cnt = self.exc_meltdown[0]
        while self.running:
            try:
                c, a = self.svr.accept()
                if self.handler(c):
                    c.close()
                em_cnt = self.exc_meltdown[0]
            except socket.timeout as e:
                pass
            except Exception as e:
                logging.warning('Unexpected exception in server accept loop', exc_info=e)
                em_cnt -= 1
                if em_cnt == 0:
                    em_cnt = 1
                    time.sleep(self.exc_meltdown[1])
        self.accepting = False

    def start(self) -> int:
        if self.svr is None:
            if self.reconnect():
                logging.warning('Unable to start server')
                return 1

        self.running = True
        self.accept_thread = threading.Thread(target=self.accept_loop)
        self.accept_thread.start()
        return 0

    def _cleanstop(self, cb: Optional[Callable[[int, Any], None]] = None) -> None:
        self.running = False
        self.accept_thread.join()
        self.svr.close()
        self.svr = None
        if cb is not None:
            cb(0, self)
        self.stopping = False

    def stop(self, cb: Optional[Callable[[int, Any], None]] = None) -> int:
        if self.stopping:
            return 1
        self.stopping = True
        cleanstop_thread = threading.Thread(target=self._cleanstop, args=(cb,))
        cleanstop_thread.start()
        return 0


class ConnectionDummyHandler:
    def __init__(self, rejecting=False) -> None:
        self.rejecting = rejecting
    def addconn(self, conn: socket.socket) -> int:
        logging.debug(f"New connection from {conn.getpeername()} (@{hex(id(conn))})")
        return 1 if self.rejecting else 0
    def dropconn(self, conn: socket.socket) -> int:
        logging.debug(f"Dropped connection from {conn.getpeername()} (@{hex(id(conn))})")
        return 0
    __call__ = addconn
