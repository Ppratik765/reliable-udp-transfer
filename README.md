# Reliable UDP Data Transfer

This is a custom implementation of a Stop-and-Wait ARQ (Automatic Repeat reQuest) protocol built on top of UDP in Python. Since UDP is inherently unreliable, this project simulates a real-world network by intentionally dropping packets and acknowledgements, and then handles those losses to guarantee data integrity during transfers.

It was built as part of a networking lab to understand how reliability layers (like TCP) work under the hood.

## How It Works

The architecture is split into a client and a server:
- **Client**: Reads an input file, chunks it into fragments (512 bytes by default), attaches a custom binary header, and sends it to the server over UDP. It waits for an acknowledgment (ACK) for every packet. If an ACK isn't received within a specific timeout, the client retransmits the packet.
- **Server**: Listens for incoming UDP packets. To simulate network instability, it deliberately drops a configurable percentage of incoming packets and outgoing ACKs. It handles duplicate packets caused by dropped ACKs, ensures everything is ordered properly, and writes the reconstructed file to disk.

### Custom Packet Header
Each packet is serialized using a strict 9-byte binary header using Python's `struct` module:
- `seq_num` (4-byte unsigned integer)
- `is_eof` (1-byte boolean)
- `payload_len` (4-byte unsigned integer)

This ensures no corruption or parsing ambiguity.

## Running the Project

You can run the full transfer loop using the provided demo script, which spins up both the server and the client in a single terminal and prints the output logs:

```bash
python run_demo.py
```

Alternatively, you can run them manually in separate terminal windows.

**1. Start the server:**
```bash
python server/server.py
```

**2. Start the client:**
```bash
python client/client.py
```

## Verifying Integrity

At the end of the transfer, both the client and server compute a SHA-256 hash of the original input file and the reconstructed output file. Even with severe simulated packet and ACK loss, these hashes will always match, proving the reliability of the Stop-and-Wait mechanism.
