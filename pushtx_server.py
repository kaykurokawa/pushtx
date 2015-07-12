# This is a server implementation of pushtx.py, where the server accepts 
# transactions to broadcast through TCP/IP
#
# USAGE:
# python pushtx_server.py <crypto>
#
import sys
import socket
import struct

import cryptoconfig
import peersockets
 
CRYPTO_MAP={'btc':'bitcoin','btc_testnet':'bitcoin_testnet','ltc':'litecoin','ltc_testnet':'litecoin_testnet',
    'doge':'dogecoin','doge_testnet':'dogecoin_testnet'}


def main():
    if len(sys.argv) < 2:
        raise Exception("invalid arguments, requires crypto as argument")

    crypto = sys.argv[1].lower()
    if crypto in CRYPTO_MAP:
        crypto=CRYPTO_MAP[crypto] 

    handler=peersockets.PeerSocketsHandler(crypto)
    while 1:
        handler.run()
  
if __name__ == "__main__":
    main()
