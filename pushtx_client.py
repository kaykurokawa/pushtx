# This is client for pushtx_server.py  
#
# USAGE:
#
# python pusthx_client.py <crypto> <tx hex>

import sys
import json
import socket

import cryptoconfig
import peersockets
import pushtx_server

SERVER_IP='localhost'
BUFFER_SIZE=500000

def _initclient(ip,port):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((ip,port))
    return s


def _communicate(ip,port,msg,recv_buffer_size):
    s=_initclient(ip,port)
    peersockets.socketsend(s,msg)
    out=peersockets.socketrecv(s,recv_buffer_size)
    s.close()
    return out

def pushtx(crypto,tx):
    crypto=crypto.lower()
    if crypto in pushtx_server.CRYPTO_MAP:
        crypto=pushtx_server.CRYPTO_MAP[crypto] 

    send_msg='tx '+tx
    recvmsg=_communicate(SERVER_IP,cryptoconfig.MESSAGING_PORT[crypto],send_msg,BUFFER_SIZE)

    if recvmsg=='ack':
        return True
    else:
        print("RECVMSG ",recvmsg)
        return False

def main():
    if len(sys.argv) < 3: 
        raise Exception('invalid arguments')
    crypto=sys.argv[1]
    tx=sys.argv[2]
    out=pushtx(crypto,tx)
    if out==False:
        print("Pushtx failed.")
    else:
        print("Pushtx succeeded.")

if __name__ == "__main__":
    main()
