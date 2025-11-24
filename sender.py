import threading
import time
import socket
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
        self.running = True

        self.rwnd = window # Flow Control (receivers advertised window)

    def start_receiving(self):
        # Starts the background thread to listen for ACKs
        t = threading.Thread(target=self._receive_loop, daemon=True)
        t.start()

    def _receive_loop(self):
        # Continuously listens for ACKs
        print("Sender listening for ACKs...")
        while self.running:
            try:
                # Check self.running periodically
                self.transport.sock.settimeout(1.0)
                try:
                    data, addr = self.transport.sock.recvfrom(4096)
                    pkt = Packet.deserialize(data)
                    if pkt and (pkt.flags & Packet.ACK):
                        self.receive_ack(pkt)
                except socket.timeout:
                    continue
            except Exception as e:
                print(f"Error in receive loop: {e}")
                break

    def send_data(self, data, addr):
        self.addr = addr
        chunks = [data[i:i+1024] for i in range(0, len(data), 1024)]

        for chunk in chunks:
            while True:
                effective_window = min(self.transport.cwnd, self.rwnd) # min(Congestion Window, Receiver Window)
                if self.next < self.base + effective_window:
                    break
                time.sleep(0.01)

            with self.lock:
                pkt = Packet(self.next, 0, Packet.ACK, 64, chunk)
                self.buffer[self.next] = pkt
                self.transport.channel.send(pkt.serialize(), addr)

                if self.base == self.next:
                    self._start_timer()

                self.next += 1
                
        # Wait for all packets to be acked before returning
        while self.base < self.next:
            time.sleep(0.1)

        # for chunk in chunks:
        #     while self.next >= self.base + self.window:
        #         time.sleep(0.01)

        #     with self.lock:
        #         pkt = Packet(self.next, 0, Packet.ACK, 64, chunk)
        #         self.buffer[self.next] = pkt
        #         self.transport.channel.send(pkt.serialize(), addr)

        #         if self.base == self.next:
        #             self._start_timer()

        #         self.next += 1

    # def receive_ack(self, ack):
    #     with self.lock:
    #         if ack > self.base:
    #             self.base = ack
    #             if self.base == self.next:
    #                 self._stop_timer()
    #             else:
    #                 self._start_timer()

    def receive_ack(self, pkt):
        ack_seq = pkt.ack
        advertised_window = pkt.window
        
        with self.lock:
            self.rwnd = advertised_window # Update Flow Control Window

            if ack_seq > self.base:
                # Cumulative ACK: everything up to ack_seq is safe
                self.base = ack_seq
                
                # CONGESTION CONTROL (TCP Tahoe/Reno Logic)
                if self.transport.cwnd < self.transport.ssthresh:
                    # Slow Start: Exponential growth
                    self.transport.cwnd += 1.0
                else:
                    # Congestion Avoidance: Linear growth
                    self.transport.cwnd += 1.0 / self.transport.cwnd
                
                print(f"ACK {ack_seq} received. CWND: {self.transport.cwnd:.2f}, RWND: {self.rwnd}")

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

    # def _on_timeout(self):
    #     """Handle timeout: retransmit all unacked packets"""
    #     with self.lock:
    #         print("[TIMEOUT] Retransmitting packets")
    #         for seq in range(self.base, self.next):
    #             if seq in self.buffer:
    #                 pkt = self.buffer[seq]
    #                 self.transport.channel.send(pkt.serialize(), self.addr)
    #         # restart timer
    #         self._start_timer()

    def _on_timeout(self):
        with self.lock:
            print("[TIMEOUT] Loss detected.")
            
            # CONGESTION CONTROL: Reaction to Loss
            self.transport.ssthresh = max(1, int(self.transport.cwnd / 2))
            self.transport.cwnd = 1.0
            print(f"Congestion Control: Dropped CWND to 1, SSTHRESH to {self.transport.ssthresh}")

            # Retransmit unacked packets
            for seq in range(self.base, self.next):
                if seq in self.buffer:
                    pkt = self.buffer[seq]
                    self.transport.channel.send(pkt.serialize(), self.addr)
            
            self._start_timer()


