import socket
import os
import random
import hashlib
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.packet import parse_data_packet, create_ack_packet

BIND_ADDR = ('127.0.0.1', 12345)
PACKET_DROP_PROB = 0.15
ACK_DROP_PROB = 0.15

def compute_sha256(filepath):
    sha = hashlib.sha256()
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()

def main():
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'received_output.txt')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(BIND_ADDR)
    
    packets_dropped = 0
    acks_dropped = 0
    duplicate_packets = 0
    
    expected_seq = 0
    file_buffer = {}
    
    print(f"[SERVER] Listening on {BIND_ADDR[0]}:{BIND_ADDR[1]}...")
    print(f"[SERVER] Simulated Packet Drop: {PACKET_DROP_PROB*100}%, ACK Drop: {ACK_DROP_PROB*100}%")

    eof_received = False
    sock.settimeout(None)

    try:
        while True:
            try:
                raw_bytes, client_addr = sock.recvfrom(2048)
            except socket.timeout:
                if eof_received:
                    print("[SERVER] Timeout after EOF. Assuming client is done.")
                    break
                else:
                    continue
            
            # Simulated packet drop
            if random.random() < PACKET_DROP_PROB:
                try:
                    seq_num, _, _ = parse_data_packet(raw_bytes)
                    print(f"[SIMULATED LOSS] Dropped Packet #{seq_num}")
                except Exception:
                    pass
                packets_dropped += 1
                continue
                
            seq_num, is_eof, data = parse_data_packet(raw_bytes)
            
            if seq_num < expected_seq:
                print(f"[SERVER] Duplicate packet #{seq_num} received, re-sending ACK.")
                duplicate_packets += 1
                # Drop through to ACK sending logic
            elif seq_num == expected_seq:
                print(f"[SERVER] Received Packet #{seq_num} (Length: {len(data)} B)")
                file_buffer[seq_num] = data
                expected_seq += 1
                if is_eof:
                    eof_received = True
                    # Set a timeout so we can exit cleanly once we're reasonably sure 
                    # the client got our final ACK.
                    sock.settimeout(2.0)
            else:
                print(f"[SERVER] Out of order packet #{seq_num} received (expected #{expected_seq}), ignoring.")
                continue

            # Simulated ACK drop
            if random.random() < ACK_DROP_PROB:
                print(f"[SIMULATED LOSS] Dropped ACK #{seq_num}")
                acks_dropped += 1
                continue
            
            ack_packet = create_ack_packet(seq_num)
            sock.sendto(ack_packet, client_addr)
            
    except KeyboardInterrupt:
        print("[SERVER] Interrupted by user.")
    finally:
        sock.close()
        
    # Reconstruct file
    print(f"\n[SERVER] Writing output to {output_file}...")
    with open(output_file, 'wb') as f:
        for i in range(expected_seq):
            if i in file_buffer:
                f.write(file_buffer[i])
                
    print("\n" + "="*40)
    print("=== Server Transfer Statistics ===")
    print("="*40)
    print(f"Number of packets deliberately dropped: {packets_dropped}")
    print(f"Number of ACKs deliberately dropped: {acks_dropped}")
    print(f"Number of duplicate packets received: {duplicate_packets}")
    
    sha256_hash = compute_sha256(output_file)
    print(f"Output file SHA-256: {sha256_hash}")
    print("="*40)

if __name__ == '__main__':
    main()
