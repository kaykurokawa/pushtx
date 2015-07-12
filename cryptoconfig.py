# Contains crypto specific parameters 


SUPPORTED_CRYPTOS   = ['bitcoin','litecoin','dogecoin','bitcoin_testnet','litecoin_testnet','dogecoin_testnet']
PROTOCOL_VERSION    = {'bitcoin': 70001,'litecoin': 70002,'dogecoin':70003, 
                        'bitcoin_testnet':70001,'litecoin_testnet':70002,
                        'dogecoin_testnet':70003}
MSG_MAGIC_BYTES     = {'bitcoin':'\xf9\xbe\xb4\xd9','litecoin':'\xfb\xc0\xb6\xdb',
                       'dogecoin':'\xc0\xc0\xc0\xc0','bitcoin_testnet':'\xfa\xbf\xb5\xda',
                       'litecoin_testnet':'\xfc\xc1\xb7\xdc',
                       'dogecoin_testnet':'\xfc\xc1\xb7\xdc'} 
PORT                = {'bitcoin':8333,'litecoin':9333,'dogecoin':22556, 
                       'bitcoin_testnet':18333 ,'litecoin_testnet':19333,
                       'dogecoin_testnet':44556}
                       # from chainparams.cpp / bitcoin source
DNS_SEEDS           = {'bitcoin' : ['dnsseed.bluematt.me','bitseed.xf2.org',
                                    'seed.bitcoin.sipa.be','dnsseed.bitcoin.dashjr.org'],
                       # from net.cpp / litecoin souce  
                       'litecoin': ["dnsseed.litecointools.com",
                                    "dnsseed.litecoinpool.org","dnsseed.ltc.xurious.com",
                                    "dnsseed.koin-project.com","dnsseed.weminemnc.com"],
                       # from chainparams.cpp / dogecoin source 
                       'dogecoin': ["seed.dogecoin.com","seed.mophides.com",
                                    "seed.dglibrary.org","seed.dogechain.info"],
                       'bitcoin_testnet':["testnet-seed.alexykot.me",
                                          "testnet-seed.bitcoin.petertodd.org",
                                          "testnet-seed.bluematt.me",
                                          "testnet-seed.bitcoin.schildbach.de"],

                       'litecoin_testnet':["testnet-seed.litecointools.com",
                                           "testnet-seed.ltc.xurious.com", 
                                           "dnsseed.wemine-testnet.com"],

                       'dogecoin_testnet':["testdoge.lionservers.de", 
                                           "testdoge-seed.lionservers.de"]
                      }
 
                      
TX_FEE_PER_KILOBYTE = {'bitcoin':10000, 'litecoin':100000 , 'dogecoin':100000000, 
                       'bitcoin_testnet':10000, 'litecoin_testnet':100000 , 'dogecoin_testnet':100000000}

MESSAGING_PORT      = {'bitcoin':1944,'litecoin':1945,'dogecoin':1946,
                       'bitcoin_testnet':1947,'litecoin_testnet':1948,'dogecoin_testnet':1949}
