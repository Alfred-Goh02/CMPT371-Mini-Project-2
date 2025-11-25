# Pipelined Reliable Transfer Protocol — Mini Project 2

This repository contains an implementation and analysis for a connection-oriented, reliable, pipelined transport protocol (course Mini-Project 2). The project implements a custom reliable transport with flow control, congestion control, and simulated loss/error for testing.

**Repository layout**

- `src/`: Python source code for the protocol and helper scripts.
  - `sender.py`, `receiver.py`, `transport.py`, `channel.py`, `packet.py` — core protocol code.
  - `run_sender.py`, `run_receiver.py`, `run_sender_2.py`, `run_receiver_2.py` — example runners for experiments.
- `Wireshark Traces/`: packet capture files used for traffic analysis (pcapng files).
- `CMPT371 Mini Project 2 Report - Alfred Goh Euluna Gotami.pdf`: project specification, protocol description, test procedures, analysis, and results.

**Assignment summary**

- **Design & Implement your protocol (40 pts):** design and implement a connection-oriented, reliable, pipelined transport protocol similar in spirit to TCP but of your own design. The implementation must include:

  - Connection establishment and teardown (connection-oriented behavior).
  - Reliable delivery with sequence numbers and ACKs.
  - Pipelining to allow multiple in-flight packets.
  - Flow control to prevent receiver buffer overflow.
  - Congestion control to respond to network conditions.

- **Analyze traffic (20 pts):** capture and analyze packet traces (e.g., with Wireshark) to demonstrate the protocol's properties:

  - Show connection setup/teardown (connection-oriented).
  - Show correct reliability (retransmissions, ACK behavior).
  - Show flow control and congestion control behavior.
  - Evaluate performance (throughput, delay) using captured traces.

- **Simulating loss/errors:** because local testing may not expose packet loss or corruption, you must simulate loss/errors (drop packets randomly, corrupt bits, etc.) in the channel layer so protocol mechanisms can be tested.

- **Bonus — Fairness (5 pts):** test your protocol coexisting with other traffic (e.g., TCP flows) and argue whether your protocol is fair.

**Deliverables**

- Source code (`.py`) — all code in `src/`.
- Packet capture(s) — `.pcapng` files in `Wireshark Traces/`.
- Report PDF — specification of the protocol, test procedures, traffic analysis, and results (`CMPT371 Mini Project 2 Report - Alfred Goh Euluna Gotami.pdf`).

These are packaged together for submission.

**How to run (basic)**

1. Open a PowerShell terminal and change to the `src` directory:

```powershell
cd .\src
```

2. Start the receiver (in one terminal):

```powershell
python .\run_receiver.py
```

3. Start the sender (in another terminal):

```powershell
python .\run_sender.py
```

4. Alternative runners: `run_sender_2.py` and `run_receiver_2.py` provide variant configurations or tests — inspect them to choose parameters.

Notes:

- If you need to see packet captures, open files in `Wireshark Traces/` with Wireshark.
- The report PDF documents protocol design, experimental setup, and the captured-traffic analysis — see it for test descriptions and expected outputs.

**Objectives to check when validating the implementation**

- Connection-oriented handshake and teardown are visible in traces.
- Retransmissions occur when simulated loss happens (reliability).
- Flow control prevents buffer overrun at receiver side.
- Congestion control reduces sending rate under loss or delay.
- Fairness experiments (bonus) show coexistence behavior.

**Next steps & tips**

- Read the report PDF for the exact spec used in this implementation.
- To exercise loss/corruption behavior, look for the simulation code in `channel.py` (random drop/corrupt flags) and tweak probabilities.
- If you want, I can add a short `RUNNING.md` with step-by-step experiment commands or help run traces and summarize results.

---

Created to summarize the assignment and point to the implementation and analysis in this repository.
