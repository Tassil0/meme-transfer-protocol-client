import socket
import pynetstring
import traceback
import sys

HOST = '159.89.4.84'
PORT = 42069
NICK = 'tassilobalbo'
AUTH_TOKEN = ''
DATA_PORT = int()

def main():
    try:
        s = init()
        auth(s)
    except KeyboardInterrupt:
        print("Shutdown requested...exiting")
    except Exception:
        traceback.print_exc(file=sys.stdout)
    sys.exit(0)


def init() -> socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.sendall(pynetstring.encode(b'C MTP V:1.0'))
    res = pynetstring.decode(s.recv(1024))
    if res == [b'S MTP V:1.0']:
        print('✅ Connection initialized')
    return s


def auth(s: socket):
    s.sendall(pynetstring.encode(b'C NICK'))
    res = pynetstring.decode(s.recv(1024))[0].decode('utf-8')
    res2 = pynetstring.decode(s.recv(1024))[0].decode('utf-8')
    AUTH_TOKEN = res.split(' ')[1]
    DATA_PORT = int(res2.split(' ')[1])
    print(AUTH_TOKEN, DATA_PORT)
    print('auth complete')


if __name__ == '__main__':
    main()
