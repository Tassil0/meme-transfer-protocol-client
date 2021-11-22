import socket
import pynetstring

HOST = '159.89.4.84'
PORT = 42069


def init():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(pynetstring.encode(b'C MTP V:1.0'))
        res = pynetstring.decode(s.recv(1024))
        if res == [b'S MTP V:1.0']:
            print('✅ Connection initialized')


if __name__ == '__main__':
    init()
