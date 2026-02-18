# Maryan Farah / N01674510

import socket
import argparse
import struct

BUF_SIZE = 4096

def run_server(port, output_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    print(f"[*] Server listening on port {port}")

    try:
        while True:
            expected_seq = 0
            buffer = {}
            f = None

            print("==== Start of reception ====")

            while True:
                data, addr = sock.recvfrom(BUF_SIZE)

                seq_num = struct.unpack('!I', data[:4])[0]

                if seq_num == 0xFFFFFFFF:
                    sock.sendto(struct.pack('!I', seq_num), addr)
                    print(f"[*] EOF received.")
                    break

                chunk = data[4:]
                sock.sendto(struct.pack('!I', seq_num), addr)

                if f is None:
                    f = open(output_file, 'wb')
                    print(f"[*] Saving as '{output_file}'")

                if seq_num == expected_seq:
                    f.write(chunk)
                    expected_seq += 1
                    while expected_seq in buffer:
                        f.write(buffer.pop(expected_seq))
                        expected_seq += 1

                elif seq_num > expected_seq:
                    if seq_num not in buffer:
                        buffer[seq_num] = chunk

            if f:
                f.close()
                print(f"[*] File saved: '{output_file}'")
            print("==== End of reception ====")

    except KeyboardInterrupt:
        print("\n[!] Server stopped.")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP File Receiver")
    parser.add_argument("--port", type=int, default=12001)
    parser.add_argument("--output", type=str, default="received_file.jpg")
    args = parser.parse_args()


    run_server(args.port, args.output)
