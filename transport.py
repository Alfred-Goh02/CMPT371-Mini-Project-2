import random
import socket
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

        self.sock.settimeout(1.0) # Timeout for handshake
        for i in range(5): # Retry up to 5 times
            try:
                print(f"Sending SYN (Attempt {i+1})...")
                self.channel.send(syn.serialize(), addr)
                data, _ = self.sock.recvfrom(4096)
                syn_ack = Packet.deserialize(data)

                if syn_ack and (syn_ack.flags & Packet.SYN) and (syn_ack.flags & Packet.ACK):
                    self.ack = syn_ack.seq + 1
                    self.seq += 1

                    ackpkt = Packet(self.seq, self.ack, Packet.ACK, 64)
                    self.channel.send(ackpkt.serialize(), addr)

                    self.state = "ESTABLISHED"
                    print("Connection Established!")
                    self.sock.settimeout(None) # Reset to blocking
                    return True
            except socket.timeout:
                print("Handshake timed out, retrying...")
        
        self.sock.settimeout(None)
        print("Failed to connect.")
        return False
    
    # TESTTTT
    def accept(self):
        """Server-side 3-way handshake"""
        print("Waiting for connection...")
        
        # 1. Wait for SYN
        while True:
            try:
                data, addr = self.sock.recvfrom(4096)
                pkt = Packet.deserialize(data)
                if pkt and (pkt.flags & Packet.SYN):
                    break # Got SYN
            except Exception:
                continue

        print("Received SYN, sending SYN-ACK...")
        
        # 2. Send SYN-ACK
        self.ack = pkt.seq + 1
        self.seq = random.randint(1, 5000)
        syn_ack = Packet(self.seq, self.ack, Packet.SYN | Packet.ACK, 64)
        self.channel.send(syn_ack.serialize(), addr)

        # 3. Wait for ACK
        self.sock.settimeout(1.0)
        for i in range(5):
            try:
                data, _ = self.sock.recvfrom(4096)
                pkt = Packet.deserialize(data)
                if pkt and (pkt.flags & Packet.ACK) and (pkt.ack == self.seq + 1):
                    self.state = "ESTABLISHED"
                    print("Connection Established!")
                    self.sock.settimeout(None)
                    return addr # Return client address
            except socket.timeout:
                print("Timeout waiting for final ACK, resending SYN-ACK...")
                self.channel.send(syn_ack.serialize(), addr)
        
        self.sock.settimeout(None)
        return None
