import struct
import hashlib


class Packet:
    HEADER_FORMAT = '!IIHH'
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    SYN = 0x01
    ACK = 0x02
    FIN = 0x04

    def __init__(self, seq, ack, flags, window, data=b''):
        self.seq = seq
        self.ack = ack
        self.flags = flags
        self.window = window
        self.data = data
        self.checksum = self.compute_checksum()

    def compute_checksum(self):
        header = struct.pack(self.HEADER_FORMAT,
                             self.seq, self.ack,
                             self.flags, self.window)
        return hashlib.md5(header + self.data).digest()[:4]

    def serialize(self):
        header = struct.pack(self.HEADER_FORMAT,
                             self.seq, self.ack,
                             self.flags, self.window)
        return header + self.checksum + self.data

    @classmethod
    def deserialize(cls, raw):
        if len(raw) < cls.HEADER_SIZE + 4:
            return None

        header = raw[:cls.HEADER_SIZE]
        seq, ack, flags, window = struct.unpack(cls.HEADER_FORMAT, header)
        checksum = raw[cls.HEADER_SIZE:cls.HEADER_SIZE + 4]
        data = raw[cls.HEADER_SIZE + 4:]

        pkt = cls(seq, ack, flags, window, data)
        if pkt.checksum != checksum:
            print("Checksum mismatch")
            return None

        return pkt
