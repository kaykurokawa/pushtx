# This is a command line interface that can be used to push raw 
# transaction (in hex) to a crypto network 

import sys
import socket
import argparse

import cryptoconfig
import peersockets

def pushtx(crypto,num_peers_to_send,tx_list,addresses):
    crypto=crypto.lower()
    if crypto not in cryptoconfig.SUPPORTED_CRYPTOS:
        raise Exception("Crypto {} not supported, suppored cryptos are {}".format(crypto,cryptoconfig.SUPPORTED_CRYPTOS)) 
    handler=peersockets.PeerSocketsHandler(crypto,tx_list,peer_list=addresses,
        num_tx_broadcasts=num_peers_to_send)

    while 1:
        handler.run()
        if all(out[1]>=num_peers_to_send for out in handler.tx_broadcast_list):
            print("FINISHED")
            return
def main():
    parser = argparse.ArgumentParser(description=
                    'Command line interface for pushtx')

    parser.add_argument('crypto_name', metavar='Crypto_Name', type=str,
                    help='Name of the cryptocurrency (Supports: {})'.format(cryptoconfig.SUPPORTED_CRYPTOS))
    parser.add_argument('-num_peers', metavar='P', type=int,
                    default=20,
                    help='Number of peers P to broadcast to')
    parser.add_argument('txs',metavar='Hex_transactions',type=str,
                    nargs='+',
                    help='List of hex transactions to broadcast')
    
    parser.add_argument('-addresses',metavar='Address',type=str,
                    nargs='?',help='Comma seperated list of addresses to connect to (do not use white space to seperate addresses)')

    args=parser.parse_args()
    crypto              = args.crypto_name.lower()
    num_peers_to_send   = args.num_peers
    tx_list             = args.txs
    addresses           = []
    if args.addresses != None:
        addresses = args.addresses.split(',')
    pushtx(crypto,num_peers_to_send,tx_list,addresses)

if __name__ == "__main__":
    main()
