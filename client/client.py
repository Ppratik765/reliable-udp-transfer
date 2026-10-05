import socket
import os
import time
import hashlib
import sys

# Add parent directory to path to import common module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.packet import create_data_packet, parse_ack_packet

SERVER_ADDR = ('127.0.0.1', 12345)
CHUNK_SIZE = 512
TIMEOUT = 1.0

def compute_sha256(filepath):
    sha = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()

def main():
    input_file = os.path.join(os.path.dirname(__file__), 'input_sample.txt')
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)

    packets_generated = 0
    total_transmitted = 0
    retransmissions = 0

    with open(input_file, 'rb') as f:
        file_data = f.read()

    # Split file contents into chunks
    chunks = [file_data[i:i+CHUNK_SIZE] for i in range(0, len(file_data), CHUNK_SIZE)]
    if not chunks:
        chunks = [b''] # Handle empty file

    for seq_num, chunk in enumerate(chunks):
        is_eof = (seq_num == len(chunks) - 1)
        packet = create_data_packet(seq_num, chunk, is_eof)
        packets_generated += 1

        attempts = 0
        while True:
            attempts += 1
            print(f"[SEND] Packet #{seq_num} (Length: {len(chunk)} B) [Attempt {attempts}]")
            sock.sendto(packet, SERVER_ADDR)
            total_transmitted += 1

            try:
                ack_bytes, _ = sock.recvfrom(1024)
                ack_num = parse_ack_packet(ack_bytes)
                if ack_num == seq_num:
                    print(f"[ACK RECV] Acknowledged Packet #{seq_num}")
                    break
                else:
                    print(f"[ACK RECV] Received out-of-order ACK #{ack_num}, expecting #{seq_num}")
            except socket.timeout:
                print(f"[TIMEOUT] Packet #{seq_num} ACK timed out. Retransmitting...")
                retransmissions += 1
            except ConnectionResetError:
                # Windows raises ConnectionResetError for UDP if the destination port is unreachable
                print(f"[TIMEOUT] Connection reset by peer (server may not be ready). Retransmitting...")
                time.sleep(1)
                retransmissions += 1
                
    sock.close()
    
    print("\n" + "="*40)
    print("=== Client Transfer Statistics ===")
    print("="*40)
    print(f"Total number of packets generated: {packets_generated}")
    print(f"Total packets transmitted: {total_transmitted}")
    print(f"Number of retransmissions: {retransmissions}")
    
    sha256_hash = compute_sha256(input_file)
    print(f"Input file SHA-256: {sha256_hash}")
    print("="*40)

if __name__ == '__main__':
    main()
