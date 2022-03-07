import socket
import pynetstring
import traceback
import sys
import base64

HOST = '159.89.4.84'
PORT = 42069
NICK = b'tassilobalbo'
AUTH_TOKEN = ''
DATA_PORT = int()

meme = 'meme.png'

def main():
    try:
        s = init()
        auth(s)
    except KeyboardInterrupt:
        print("Shutdown requested...exiting")
    except Exception:
        traceback.print_exc(file=sys.stdout)
    sys.exit(0)


def recvStr(s: socket) -> str:
    return pynetstring.decode(s.recv(1024))[0].decode('utf-8').split(' ')[1]


def init() -> socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.sendall(pynetstring.encode(b'C MTP V:1.0'))
    print("msg with version sent")
    res = pynetstring.decode(s.recv(1024))
    if res == [b'S MTP V:1.0']:
        print('✅ Connection initialized')
    return s


def auth(s: socket):
    s.sendall(pynetstring.encode(b'C ' + NICK))
    res = pynetstring.decode(s.recv(1024))[0].decode('utf-8')
    res2 = pynetstring.decode(s.recv(1024))[0].decode('utf-8')
    AUTH_TOKEN = res.split(' ')[1]
    DATA_PORT = int(res2.split(' ')[1])
    print(AUTH_TOKEN, DATA_PORT)
    print('auth complete')
    # Open Data Channel
    dataChannel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dataChannel.connect((HOST, DATA_PORT))
    dataChannel.sendall(pynetstring.encode(b'C ' + NICK))
    print('Data Channel auth response: ' + recvStr(dataChannel))
    handleReq(dataChannel)


def handleReq(s):
    for i in range(4):
        res = recvStr(s)
        print(res)
        if res == 'REQ:meme':
            sendMeme(s, meme)
            print('meme sent')
        elif res == 'REQ:description':
            s.sendall(pynetstring.encode(b'C test'))
            print('description sent')
        elif res == 'REQ:isNSFW':
            s.sendall(pynetstring.encode(b'C false'))
            print('nsfw sent')
        elif res == 'REQ:password':
            s.sendall(pynetstring.encode(b'C kokos'))
            print('pass sent')
        print('datalength: ', pynetstring.decode(s.recv(1024)))
    print('dtoken: ', pynetstring.decode(s.recv(1024)))

def sendMeme(s, meme):
    with open(meme, 'rb') as f:
        data = base64.b64encode(f.read())
    s.sendall(pynetstring.encode(b'C ' + data))

if __name__ == '__main__':
    main()
