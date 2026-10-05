import struct

# Header: seq_num (4 bytes), is_eof (1 byte), payload_len (4 bytes)
HEADER_FORMAT = '!I?I'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
ACK_FORMAT = '!I'
ACK_SIZE = struct.calcsize(ACK_FORMAT)

def create_data_packet(seq_num: int, data: bytes, is_eof: bool) -> bytes:
    """Encapsulates the data into a binary packet with a header."""
    header = struct.pack(HEADER_FORMAT, seq_num, is_eof, len(data))
    return header + data

def parse_data_packet(raw_bytes: bytes) -> tuple[int, bool, bytes]:
    """Extracts sequence number, EOF flag, and payload from a raw packet."""
    header = raw_bytes[:HEADER_SIZE]
    seq_num, is_eof, payload_len = struct.unpack(HEADER_FORMAT, header)
    data = raw_bytes[HEADER_SIZE:HEADER_SIZE+payload_len]
    return seq_num, is_eof, data

def create_ack_packet(ack_num: int) -> bytes:
    """Creates an acknowledgement packet."""
    return struct.pack(ACK_FORMAT, ack_num)

def parse_ack_packet(raw_bytes: bytes) -> int:
    """Parses an acknowledgement packet to get the ACK number."""
    ack_num, = struct.unpack(ACK_FORMAT, raw_bytes[:ACK_SIZE])
    return ack_num
