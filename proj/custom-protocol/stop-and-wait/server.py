import socket
import struct
import random

# 1. Setup the address and port (like a phone number)
UDP_IP = "127.0.0.1"  # Means "this local computer"
UDP_PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"📡 Server is alive and listening on port {UDP_PORT}...")
print("⚠️ Warning: Internet simulator active. 30% of packets will be dropped!")

expected_seq = 1

while True:
    # 2. Grab the raw bytes out of the air
    raw_data, addr = sock.recvfrom(1024)
    
    # 3. Simulate the chaotic internet (Drop 30% of packets)
    if random.random() < 0.3:
        print("🔥 [Internet Chaos] A packet was lost in the wires! Ignoring it.")
        continue

    # 4. Unpack the 8-byte header ('I' = 4-byte unsigned integer)
    header_format = "!II"
    header_bytes = raw_data[:8]
    payload_bytes = raw_data[8:]
    
    seq_num, flag = struct.unpack(header_format, header_bytes)
    message = payload_bytes.decode('utf-8')
    
    print(f"📥 Received Packet #{seq_num} containing: '{message}'")
    
    # 5. Process the data and send a receipt (ACK) back to the sender
    if flag == 1:  # 1 means Data Packet
        # Build an ACK packet (Flag = 2)
        ack_header = struct.pack(header_format, seq_num, 2)
        sock.sendto(ack_header, addr)
        print(f"📤 Sent ACK receipt for Packet #{seq_num}")
