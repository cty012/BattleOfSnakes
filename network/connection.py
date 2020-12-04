from collections import deque
from typing import *
import logging
import socket
import time
import threading


class MessageParser:
    def parse_send(self, msg: bytes, buf: bytes) -> bytes:
        ...

    def parse_recv(self, buf: bytes) -> Tuple[bytes, bytes]:
        ...


class Connection:
    def __init__(self, conn, parser, *, recv_chunk=1024, timeout=1.0, exc_meltdown=(3, 2.0)) -> None:
        """
        :param conn: Socket of the connection
        :type conn: socket.socket
        :param parser:
        :type parser: MessageParser
        :param recv_chunk:
        :type recv_chunk: int
        :param timeout:
        :type timeout: Union[int, float]
        :param exc_meltdown:
        :type exc_meltdown: Tuple[int, Union[int, float]]
        """
        self.conn = conn
        self.parser = parser
        self.recv_chunk = recv_chunk
        self.timeout = timeout
        self.exc_meltdown = exc_meltdown

        self.sendbuf = b''
        self.recvbuf = b''
        self.recv_thread = None
        self.sending = False
        self.recving = False
        self.stopping = False

        self.recvqueue = deque()

    def send(self, msg: Optional[bytes] = None):
        """
        :param msg:
        :type msg: Optional[bytes]
        :returns: status (0: normal, >0: error)
        :rtype: int
        """
        if self.stopping or not self.sending:
            return 1
        if msg is not None:
            self.sendbuf = self.parser.parse_send(msg, self.sendbuf)
        while self.sendbuf:
            try:
                l = self.conn.send(self.sendbuf)
                self.sendbuf = self.sendbuf[l:]
            except Exception as e:
                logging.warning(f"ClientConnection {self.conn.getpeername()} send met unexpected exception; {len(self.sendbuf)} bytes unsent", exc_info=e)
                return 1
        return 0

    def recv(self) -> Optional[bytes]:
        if self.recvqueue:
            return self.recvqueue.popleft()
        return None

    def recv_all(self) -> List[bytes]:
        return [self.recvqueue.popleft() for i in range(len(self.recvqueue))]

    def recv_loop(self) -> None:
        self.recving = True
        em_cnt = self.exc_meltdown[0]
        while not self.stopping:
            try:
                self.recvbuf += self.conn.recv(self.recv_chunk)
                while 1:
                    msg, recvbuf = self.parser.parse_recv(self.recvbuf)
                    if msg is not None:
                        self.recvqueue.append(msg)
                    if len(self.recvbuf) == len(recvbuf):  # No read
                        break
                    self.recvbuf = recvbuf
                em_cnt = self.exc_meltdown[0]
            except socket.timeout as e:
                pass
            except Exception as e:
                logging.warning(f"ClientConnection {self.conn.getpeername()} recv met unexpected exception", exc_info=e)
                em_cnt -= 1
                if em_cnt == 0:
                    em_cnt = 1
                    time.sleep(self.exc_meltdown[1])
        self.recving = False
        logging.debug(f"ClientConnection {self.conn.getpeername()} exiting with {len(self.recvbuf)} unparsed bytes")

    def start(self) -> int:
        self.conn.settimeout(self.timeout)
        self.recv_thread = threading.Thread(target=self.recv_loop)
        self.recv_thread.start()
        self.sending = True
        return 0

    def _cleanstop(self, cb: Optional[Callable[[int, Any], None]] = None) -> None:
        self.sending = False
        self.recv_thread.join()
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


class MessageDummyParser:
    def __init__(self, conn: Connection = None, clear=True, encoding='utf-8') -> None:
        self.conn = conn
        self.clear = clear
        self.encoding = encoding

    def parse_send(self, msg: bytes, buf: bytes) -> bytes:
        logging.debug(f"Appending {msg} to send buffer to {self.conn.conn.getpeername()}")
        return bytes(buf + msg, encoding=self.encoding)  # Encoding cast

    def parse_recv(self, buf: bytes) -> Tuple[bytes, bytes]:
        logging.debug(f"Message from {self.conn.conn.getpeername() if self.conn else '-'} : {buf.decode(self.encoding).__repr__()}")
        return buf, (b'' if self.clear else buf)
