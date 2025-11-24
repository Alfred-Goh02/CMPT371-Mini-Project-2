import random
from packet import Packet
from channel import UnreliableChannel

class ReliableTransport:
    def __init__(self, sock, loss_rate=0.1):
        self.sock = sock
        self.channel = UnreliableChannel(sock, loss_rate)
        self.seq = random.randint(1, 5000)
        self.ack = 0
        self.cwnd = 1
        self.ssthresh = 32
        self.state = "CLOSED"

    def connect(self, addr):
        """3-way handshake"""
        syn = Packet(self.seq, 0, Packet.SYN, 64)
        self.channel.send(syn.serialize(), addr)

        data, _ = self.sock.recvfrom(4096)
        syn_ack = Packet.deserialize(data)

        if syn_ack and (syn_ack.flags & Packet.SYN) and (syn_ack.flags & Packet.ACK):
            self.ack = syn_ack.seq + 1
            self.seq += 1

            ackpkt = Packet(self.seq, self.ack, Packet.ACK, 64)
            self.channel.send(ackpkt.serialize(), addr)

            self.state = "ESTABLISHED"
            return True
        return False
