import random


class UnreliableChannel:
    def __init__(self, sock, loss_rate=0.1, corrupt_rate=0.05):
        self.sock = sock
        self.loss_rate = loss_rate
        self.corrupt_rate = corrupt_rate

    def send(self, data, addr):
        if random.random() < self.loss_rate:
            print("[LOSS] Packet dropped")
            return

        if random.random() < self.corrupt_rate:
            print("[CORRUPT] Packet corrupted")
            data = self._corrupt_data(data)

        self.sock.sendto(data, addr)

    def _corrupt_data(self, data):
        d = bytearray(data)
        if len(d) > 0:
            idx = random.randint(0, len(d) - 1)
            d[idx] ^= 0xFF
        return bytes(d)
