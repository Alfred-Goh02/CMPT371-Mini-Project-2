import socket
from transport import ReliableTransport
from sender import GBNSender

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 0))
rt = ReliableTransport(sock, loss_rate=0.2)
sender = GBNSender(rt)

addr = ('127.0.0.1', 9001)

print("Connecting...")
rt.connect(addr)

print("Sending...")
data = b'A' * 50000
sender.send_data(data, addr)

print("Done.")
