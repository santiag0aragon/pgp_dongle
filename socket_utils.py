import socket
import struct


def recv_one_message(sock):
    lengthbuf = recvall(sock, 4)
    length, = struct.unpack('!L', lengthbuf)
    lengthbuf = recvall(sock, 4)
    mode, = struct.unpack('!L', lengthbuf)
    data = {'mode': mode,
            'data': recvall(sock, length)}
    return data


def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf


def send_one_upload_key(sock, data):
    send_one_message(sock, data, 6)


def send_one_search_key(sock, data):
    send_one_message(sock, data, 5)


def send_one_sgn(sock, data):
    send_one_message(sock, data, 4)


def send_one_vrf(sock, data):
    send_one_message(sock, data, 3)


def send_one_resp(sock, data):
    send_one_message(sock, data, 2)


def send_one_dec(sock, data):
    send_one_message(sock, data, 1)


def send_one_enc(sock, data):
    send_one_message(sock, data, 0)


def send_one_message(sock, data, mode):
    length = len(data)
    sock.sendall(struct.pack('!L', length))
    sock.sendall(struct.pack('!L', mode))
    sock.sendall(data)
