import socket
import struct
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1.0) # ⏱️ If we don't hear back in 1 second, stop waiting!

# The data we want to send over our custom protocol
messages_to_send = ["Hello World!", "Networking is cool.", "Building protocols is fun!"]
header_format = "!II" # Two 4-byte integers

for index, text in enumerate(messages_to_send):
    seq_num = index + 1
    payload = text.encode('utf-8')
    
    # Pack variables into raw binary bytes (Flag = 1 for Data)
    header = struct.pack(header_format, seq_num, 1)
    packet = header + payload
    
    acked = False
    attempts = 0
    
    # Keep trying until the server sends a receipt
    while not acked:
        attempts += 1
        print(f"🚀 Sending Packet #{seq_num} (Attempt {attempts}): '{text}'")
        sock.sendto(packet, (UDP_IP, UDP_PORT))
        
        try:
            # Wait and listen for the server's ACK receipt
            ack_data, addr = sock.recvfrom(1024)
            ack_seq, ack_flag = struct.unpack(header_format, ack_data[:8])
            
            if ack_flag == 2 and ack_seq == seq_num:
                print(f"✅ Success! Server received Packet #{seq_num}\n")
                acked = True
                
        except socket.timeout:
            # 🚨 The stopwatch hit 1.0 second! 
            print(f"⏰ Timeout! No receipt for Packet #{seq_num}. Trying again...")
            time.sleep(0.5) # Wait a brief moment before flooding the network

print("🎉 All data sent successfully through our custom protocol!")
