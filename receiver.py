from packet import Packet

class Receiver:
    def __init__(self, transport):
        self.transport = transport
        self.expected = 0

    def handle_packet(self, pkt, addr):
        if pkt.flags & Packet.SYN:
            return self.transport.handle_handshake(pkt, addr)

        if pkt.seq == self.expected:
            self.expected += 1
            ack = Packet(0, self.expected, Packet.ACK, 64)
            self.transport.channel.send(ack.serialize(), addr)
            return pkt.data

        else:
            ack = Packet(0, self.expected, Packet.ACK, 64)
            self.transport.channel.send(ack.serialize(), addr)
            return None
