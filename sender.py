import threading
import time
from packet import Packet

class GBNSender:
    def __init__(self, transport, window=10):
        self.transport = transport
        self.window = window
        self.base = 0
        self.next = 0
        self.buffer = {}
        self.timeout = 1.0
        self.timer = None
        self.addr = None
        self.lock = threading.Lock()

    def send_data(self, data, addr):
        self.addr = addr
        chunks = [data[i:i+1024] for i in range(0, len(data), 1024)]

        for chunk in chunks:
            while self.next >= self.base + self.window:
                time.sleep(0.01)

            with self.lock:
                pkt = Packet(self.next, 0, Packet.ACK, 64, chunk)
                self.buffer[self.next] = pkt
                self.transport.channel.send(pkt.serialize(), addr)

                if self.base == self.next:
                    self._start_timer()

                self.next += 1

    def receive_ack(self, ack):
        with self.lock:
            if ack > self.base:
                self.base = ack
                if self.base == self.next:
                    self._stop_timer()
                else:
                    self._start_timer()



    def _start_timer(self):
        """Start a retransmission timer if not already running"""
        if self.timer is not None:
            self.timer.cancel()  # stop old timer
        self.timer = threading.Timer(self.timeout, self._on_timeout)
        self.timer.start()

    def _stop_timer(self):
        """Stop the timer"""
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None

    def _on_timeout(self):
        """Handle timeout: retransmit all unacked packets"""
        with self.lock:
            print("[TIMEOUT] Retransmitting packets")
            for seq in range(self.base, self.next):
                if seq in self.buffer:
                    pkt = self.buffer[seq]
                    self.transport.channel.send(pkt.serialize(), self.addr)
            # restart timer
            self._start_timer()
