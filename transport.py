import random
import time
from packet import Packet

class ReliableTransport:
    def __init__(self, sock, loss_rate=0.1):
        self.sock = sock
        self.loss_rate = loss_rate
        from channel import UnreliableChannel
        self.channel = UnreliableChannel(sock, loss_rate)

        self.seq = random.randint(1, 5000)
        self.state = "CLOSED"

    # ==========================
    # CLIENT SIDE CONNECT()
    # ==========================
    def connect(self, addr, timeout=2):
        print("[RT] Sending SYN")
        syn = Packet(self.seq, 0, Packet.SYN, 64)
        self.channel.send(syn.serialize(), addr)

        self.sock.settimeout(timeout)
        try:
            data, server = self.sock.recvfrom(4096)
        except:
            print("[RT] SYN timeout — connection failed.")
            return False

        syn_ack = Packet.deserialize(data)
        if not syn_ack:
            print("[RT] Invalid SYN+ACK")
            return False

        if not (syn_ack.flags & Packet.SYN and syn_ack.flags & Packet.ACK):
            print("[RT] Not SYN+ACK")
            return False

        print("[RT] Received SYN+ACK")

        self.seq += 1
        ackpkt = Packet(self.seq, syn_ack.seq + 1, Packet.ACK, 64)
        print("[RT] Sending final ACK")
        self.channel.send(ackpkt.serialize(), addr)

        self.state = "ESTABLISHED"
        print("[RT] Connection established")
        return True

    # ==========================
    # SERVER SIDE HANDSHAKE
    # ==========================
    def handle_handshake(self, pkt, addr):
        if pkt.flags & Packet.SYN:
            print("[RT] Received SYN from client")

            syn_ack = Packet(random.randint(1, 5000),
                             pkt.seq + 1,
                             Packet.SYN | Packet.ACK,
                             64)

            print("[RT] Sending SYN+ACK")
            self.channel.send(syn_ack.serialize(), addr)
            return "WAIT_FOR_ACK", syn_ack.seq

        return ("INVALID", None)
