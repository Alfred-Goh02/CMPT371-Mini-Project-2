import socket
from transport import ReliableTransport
from sender import GBNSender

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 0))

# Initialize transport with 20% loss to test congestion control
rt = ReliableTransport(sock, loss_rate=0.1) # CHANGE THIS BACKKKKKKKKKK
sender = GBNSender(rt)

addr = ('127.0.0.1', 9002)

print("Connecting...")
if rt.connect(addr):
    print("Sending...")

    sender.start_receiving() # Start thread to listen for ACKs

    # send 50,000 bytes
    data = b'A' * 50000
    sender.send_data(data, addr)

    print("Done.")
else:
    print("Could not connect to receiver.")
