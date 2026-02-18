# This program was modified by Maryan Farah / N01674510

import socket
import argparse
import os
import struct

CHUNK_SIZE = 4092
TIMEOUT = 0.1
MAX_RETRIES = 30

def run_client(target_ip, target_port, input_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)
    server_address = (target_ip, target_port)

    print(f"[*] Sending file '{input_file}' to {target_ip}:{target_port}")

    if not os.path.exists(input_file):
        print(f"[!] Error: File '{input_file}' not found.")
        return

    try:
        with open(input_file, 'rb') as f:
            seq_num = 0
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break

                packet = struct.pack('!I', seq_num) + chunk

                for attempt in range(MAX_RETRIES):
                    sock.sendto(packet, server_address)
                    try:
                        ack, _ = sock.recvfrom(8)
                        if struct.unpack('!I', ack)[0] == seq_num:
                            break
                    except socket.timeout:
                        pass
                else:
                    print(f"[!] Failed to send packet {seq_num} after {MAX_RETRIES} retries")
                    return

                seq_num += 1

        for attempt in range(MAX_RETRIES):
            sock.sendto(struct.pack('!I', 0xFFFFFFFF), server_address)
            try:
                sock.recvfrom(8)
                break
            except socket.timeout:
                pass

        print("[*] File transmission complete.")

    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP File Sender")
    parser.add_argument("--target_ip", type=str, default="127.0.0.1")
    parser.add_argument("--target_port", type=int, default=12000)
    parser.add_argument("--file", type=str, required=True)
    args = parser.parse_args()

    run_client(args.target_ip, args.target_port, args.file)