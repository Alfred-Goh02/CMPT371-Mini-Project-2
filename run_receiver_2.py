import socket
from transport import ReliableTransport
from receiver import Receiver
from packet import Packet

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 9002))

rt = ReliableTransport(sock, loss_rate=0.2)
rx = Receiver(rt)

print("Receiver starting...")
client_addr = rt.accept() # Wait for handshake
if not client_addr:
    print("Handshake failed.")
    exit()

print("Receiver ready...")

while True:
    data, addr = sock.recvfrom(4096)
    pkt = Packet.deserialize(data)
    if pkt:
        result = rx.handle_packet(pkt, addr)
        if result:
            print("Received:", len(result), "bytes")
