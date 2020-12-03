class Parser:
    def __init__(self, bytes=b''):
        self.bytes = bytes

    def _parse(self):
        if len(self.bytes) < 10:
            return None
        length, bytes_rest = int(self.bytes[:10].decode('utf-8')), self.bytes[10:]
        if len(bytes_rest) < length:
            return None
        result, self.bytes = bytes_rest[:length].decode('utf-8'), bytes_rest[length:]
        return result

    def parse(self, new_bytes):
        self.bytes += new_bytes
        results = []
        while True:
            result = self._parse()
            if result is None:
                break
            results.append(result)
        return results
