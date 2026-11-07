import socket
import struct
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(False)  # ⚡ Crucial: don't freeze when listening for ACKs!

# Generate a larger pool of data to see the concurrency in action
messages = [f"Data Chunk {i}" for i in range(1, 11)]
total_packets = len(messages)

WINDOW_SIZE = 3  # How many packets can fly through the air concurrently
TIMEOUT_INTERVAL = 1.0  # Seconds before re-sending a packet

header_format = "!II"
window_base = 1
next_seq_num = 1

# Track timers and packet bytes: {seq_num: (raw_packet_bytes, send_time)}
sent_packets = {}
acked_packets = set()

print(f"🚀 Starting Sliding Window Client (Size: {WINDOW_SIZE}). Sending {total_packets} packets...")

while window_base <= total_packets:
    
    # 1. TRANSMIT: Blast out new packets concurrently up to our window limit
    while next_seq_num < window_base + WINDOW_SIZE and next_seq_num <= total_packets:
        text = messages[next_seq_num - 1]
        payload = text.encode('utf-8')
        header = struct.pack(header_format, next_seq_num, 1)
        packet = header + payload
        
        sock.sendto(packet, (UDP_IP, UDP_PORT))
        sent_packets[next_seq_num] = (packet, time.time())
        print(f"✈️  Blasted Packet #{next_seq_num} concurrently.")
        next_seq_num += 1

    # 2. LISTEN FOR ACKS: Check the sky for receipts (Non-blocking)
    try:
        ack_data, addr = sock.recvfrom(1024)
        ack_seq, ack_flag = struct.unpack(header_format, ack_data[:8])
        
        if ack_flag == 2 and ack_seq >= window_base:
            acked_packets.add(ack_seq)
            print(f"📥 Got ACK receipt for Packet #{ack_seq}")
            
            # If the oldest packet in our window was ACKed, slide the window base forward!
            while window_base in acked_packets:
                print(f"🟩 [WINDOW SLIDE] Base advanced past Packet #{window_base}")
                if window_base in sent_packets:
                    del sent_packets[window_base]  # Clear memory
                window_base += 1
                
    except BlockingIOError:
        # No ACKs were waiting in the system buffer right now, keep moving
        pass

    # 3. MANAGE TIMEOUTS: Check if any un-ACKed packet has been flying too long
    current_time = time.time()
    for seq, (packet, send_time) in sent_packets.items():
        if seq not in acked_packets and (current_time - send_time) > TIMEOUT_INTERVAL:
            print(f"⏰ Timeout! Packet #{seq} lost. Re-transmitting...")
            sock.sendto(packet, (UDP_IP, UDP_PORT))
            sent_packets[seq] = (packet, current_time)  # Reset its stopwatch

    time.sleep(0.05)  # Tiny pause to avoid melting your CPU core in the loop

print("\n🎉 Mission Accomplished! All packets reliably sent and ordered using a Sliding Window protocol!")
