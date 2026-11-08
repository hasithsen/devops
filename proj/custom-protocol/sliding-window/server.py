import socket
import struct
import random

UDP_IP = "127.0.0.1"
UDP_PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"📡 Sliding Window Server listening on port {UDP_PORT}...")
print("⚠️ 30% Packet Loss Simulator Active!")

header_format = "!II"
expected_seq = 1
received_buffer = {}  # Holds out-of-order packets: {seq_num: message}

while True:
    raw_data, addr = sock.recvfrom(1024)
    
    # 1. Simulate packet loss
    if random.random() < 0.3:
        print("🔥 [Chaos] Dropped an incoming packet!")
        continue

    # 2. Unpack header and payload
    seq_num, flag = struct.unpack(header_format, raw_data[:8])
    message = raw_data[8:].decode('utf-8')
    
    # 3. Always ACK any data packet we successfully receive
    if flag == 1:
        ack_packet = struct.pack(header_format, seq_num, 2)
        sock.sendto(ack_packet, addr)
        print(f"📤 Received Packet #{seq_num}. Sent ACK #{seq_num}")

        # If it's a new packet we haven't processed yet, buffer it
        if seq_num >= expected_seq and seq_num not in received_buffer:
            received_buffer[seq_num] = message

        # 4. Slide the receiving window forward!
        # Check if the packet we are waiting for has arrived (either just now or previously buffered)
        while expected_seq in received_buffer:
            final_msg = received_buffer.pop(expected_seq)
            print(f"✅ [WINDOW SLIDE] Delivering Packet #{expected_seq} to App: '{final_msg}'")
            expected_seq += 1
