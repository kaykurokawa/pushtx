Pushtx by Umpei Kay Kurokawa
v 0.0 

INTRODUCTION:

This tools is for pushing transactions out into various cryptocurrency networks.

Coded with Python 2.7 and tested with Ubuntu 12.04/14.04. No support for Python 3 yet.  


CURRENT FEATURES:

Connect to Bitcoin/Litecoin/Dogecoin/Dashpay nodes and broadcast transactions 

USAGE:

pushtx.py [-h] [-num_peers P] [-addresses [Address]]
                 Crypto_Name Hex_transactions [Hex_transactions ...]

Command line interface for pushtx

positional arguments:
  Crypto_Name           Name of the cryptocurrency (Supports: ['bitcoin',
                        'litecoin', 'dogecoin','dashpay', 'bitcoin_testnet',
                        'litecoin_testnet', 'dogecoin_testnet','dashpay_testnet'])
  Hex_transactions      List of hex transactions to broadcast

optional arguments:
  -h, --help            show this help message and exit
  -num_peers P          Number of peers P to broadcast to
  -addresses [Address]  Comma seperated list of addresses to connect to (do
                        not use white space to seperate addresses)

Example: python pushtx.y bitcoin [transation in hex]

This will connect to crypto nodes and broadcast the transactions. Note that there is no check done on the transaction's validity, so this is useful for sending some transactions that would be labeled as invalid by bitcoind or blockchain.info's pushtx (i.e, tx's utilizing OP_RETURN).


You can also use pushtx_server.py to keep peer connections open and than use pushtx_client.py to push out new transactions for better efficiency.


KNOWN ISSUES:

Please submit any issues you find at https://github.com/kaykurokawa/pushtx/issues



