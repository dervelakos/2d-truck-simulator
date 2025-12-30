import socket
import struct

from MiddlewareBuffer import MiddlewareBuffer

class InputDataStream:
    def __init__(self, group: str, port: int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Allow multiple programs to listen on the same port
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind to the port on all interfaces
        self.sock.bind(('', port))

        mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        print(f"Listening on multicast group {group}:{port}...")

    def recv(self, size):
        buffer = MiddlewareBuffer(dataLen=size, headerLen=1)

        nbytes = self.sock.recv_into(buffer.buff, size+1)
        print(f"Received {nbytes} bytes into buffer. dataOffset={buffer.dataOffset}")
        print(f"Buffer contents (header+data): {buffer.buff[:buffer.dataOffset]}")

        return buffer

    def close(self):
        self.sock.close()

class OutputDataStream:
    def __init__(self, group: str, port: int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        ttl = struct.pack('b', 1)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

        self.group = group
        self.port = port

        self.seqId = 0

    def getBuffer(self, size):
        return MiddlewareBuffer(dataLen=size, headerLen=1)

    def send(self, buffer: MiddlewareBuffer) -> None:
        if buffer is None:
            return

        bytes_sent = self.sock.sendto(buffer.getBytes(), (self.group, self.port))
        if bytes_sent != buffer.getSize():
            print(f"Warning: only {bytes_sent}/{buffer.getSize()} bytes were sent")

class Middleware:
    def __init__(self):
        pass

