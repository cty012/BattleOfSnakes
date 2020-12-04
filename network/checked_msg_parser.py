import hashlib


MD5_SIZE = 16


class CheckedMsgParser:
    '''
    `CheckedMsgParser` parses byte messages in the format

    `<align_anchor: bytes><length: byte-coded int><message><md5: bytes>`

    `CheckedMsgParser` should be used alongside `ClientConnection`
    '''
    def __init__(self, *, encoding='utf-8', lengthlen=2, align_anchor=b'[TATA]'):
        """
        :param encoding:
        :type encoding: str
        :param lengthlen:
        :type lengthlen: int
        :param align_anchor:
        :type align_anchor: bytes
        """
        self.encoding = encoding
        self.lengthlen = lengthlen
        self.align_anchor = align_anchor
        self.anchorlen = len(self.align_anchor)

        self.recv_aligned = False

    def parse_send(self, msg: bytes, buf: bytes) -> bytes:
        msglen = len(msg)
        prefix = int2bytes(msglen, self.lengthlen)
        suffix = hashlib.md5(msg).digest()
        return bytes(buf + self.align_anchor + prefix + msg + suffix, encoding=self.encoding)

    def _align_recv(self, buf: bytes) -> bytes:
        if self.align_anchor in buf:
            idx = buf.index(self.align_anchor)
            buf = buf[idx:]  # Keep anchor
            self.recv_aligned = True
        return buf

    def parse_recv(self, buf: bytes):
        """
        :rtype Tuple[Optional[bytes], bytes]
        """
        if not self.recv_aligned:
            buf = self._align_recv(buf)
        if not self.recv_aligned:
            return None, buf

        if len(buf) < self.lengthlen:
            return None, buf
        msglen = bytes2int(buf[self.anchorlen : self.anchorlen + self.lengthlen])
        if len(buf) < self.lengthlen + msglen + MD5_SIZE:
            return None, buf

        msg = buf[self.anchorlen + self.lengthlen : self.anchorlen + self.lengthlen + msglen]
        h1 = hashlib.md5(msg).digest()
        h2 = buf[self.anchorlen + self.lengthlen + msglen : self.anchorlen + self.lengthlen + msglen + MD5_SIZE]

        self.recv_aligned = False  # Anchor used up; no guarantee for alignment next time
        if h1 != h2:  # Message corrupted
            return None, buf[self.anchorlen:]  # Remove current anchor
        return msg, buf[self.anchorlen + self.lengthlen + msglen + MD5_SIZE]  # Remove entire message
