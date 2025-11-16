#!/usr/bin/env python3
"""
client.py - Improved framed client with retries and verbose diagnostics.

Usage examples:
  python client.py --host 1.2.3.4 --port 15156 --op 6 --timeout 20 --retries 3 --verbose
"""
import socket, struct, argparse, sys, time

HDR_FMT = "<II"
RESP_HDR_FMT = "<II"

def hexdump(b: bytes) -> str:
    return b.hex()

DEFAULT_TIMEOUT = 6.0

class KernelClient:
    def __init__(self, host="127.0.0.1", port=1337, timeout=DEFAULT_TIMEOUT, verbose=False):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.verbose = verbose
        self.sock = None

    def connect(self):
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
        if self.verbose:
            print(f"[+] connecting to {self.host}:{self.port} (timeout={self.timeout})")
        s = socket.create_connection((self.host, self.port), timeout=self.timeout)
        self.sock = s
        if self.verbose:
            print("[+] connected")
        return s

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None

    def _send(self, op, data=b""):
        if not self.sock:
            self.connect()
        hdr = struct.pack(HDR_FMT, op, len(data))
        self.sock.sendall(hdr + data)

    def _recv_all(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                break
            buf += chunk
        return buf

    def _recv_resp(self):
        hdr = self._recv_all(struct.calcsize(RESP_HDR_FMT))
        if not hdr:
            raise ConnectionError("no response header (connection closed or timed out)")
        status, size = struct.unpack(RESP_HDR_FMT, hdr)
        data = self._recv_all(size) if size else b""
        return status, data

    def op_raw(self, op, payload=b""):
        self._send(op, payload)
        return self._recv_resp()

    # helpers
    def create(self, size, data=b""):
        return self.op_raw(1, struct.pack("<I", size) + data)

    def free(self, identifier=b""):
        return self.op_raw(2, identifier)

    def setbuf(self, data=b""):
        return self.op_raw(3, data)

    def trigger(self, identifier=b""):
        return self.op_raw(4, identifier)

    def spray(self, count, size, pattern=b"A"):
        payload = struct.pack("<II", count, size) + (pattern * size)
        return self.op_raw(5, payload)

    def leak(self):
        return self.op_raw(6, b"")

    def readflag(self):
        return self.op_raw(7, b"")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=1337)
    ap.add_argument("--op", type=int, help="single op to send (1..7)")
    ap.add_argument("--data", help="hex (0x...) or ascii payload")
    ap.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    ap.add_argument("--retries", type=int, default=1)
    ap.add_argument("--wait", type=float, default=1.0, help="seconds between retries")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    payload = b""
    if args.data:
        if args.data.startswith("0x"):
            payload = bytes.fromhex(args.data[2:])
        else:
            payload = args.data.encode()

    client = KernelClient(args.host, args.port, timeout=args.timeout, verbose=args.verbose)

    for attempt in range(1, args.retries + 1):
        try:
            client.connect()
            if args.op is None:
                print(f"Connected to {args.host}:{args.port}. Use --op to send a request.")
                client.close()
                return
            status, data = client.op_raw(args.op, payload)
            print("STATUS:", status)
            print("DATA(len={}):".format(len(data)))
            print(hexdump(data))
            try:
                print(data.decode(errors="replace"))
            except:
                pass
            client.close()
            return
        except (ConnectionRefusedError, socket.timeout) as e:
            print(f"[!] attempt {attempt}/{args.retries} failed: {e}")
            client.close()
            if attempt < args.retries:
                time.sleep(args.wait)
                continue
            print("[!] giving up after retries")
            sys.exit(2)
        except Exception as e:
            print("[!] unexpected error:", e)
            client.close()
            sys.exit(3)

if __name__ == "__main__":
    main()
