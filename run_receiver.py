import socket
from packet import Packet
from receiver import Receiver
from transport import ReliableTransport

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 9001))

rt = ReliableTransport(sock)
receiver = Receiver(rt)

handshake_done = False

print("Server listening...")

while True:
    data, addr = sock.recvfrom(4096)
    pkt = Packet.deserialize(data)
    if not pkt:
        continue

    # ==========================
    # HANDLE HANDSHAKE
    # ==========================
    if not handshake_done:
        state, synack_seq = rt.handle_handshake(pkt, addr)

        if state == "WAIT_FOR_ACK":
            print("[SERVER] Waiting for final ACK...")
            continue

        # Client final ACK
        if pkt.flags & Packet.ACK:
            print("[SERVER] Handshake complete!")
            handshake_done = True
        continue

    # ==========================
    # DATA PHASE
    # ==========================
    receiver.handle_packet(pkt, addr)
