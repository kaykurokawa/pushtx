# Contains crypto specific parameters 


SUPPORTED_CRYPTOS   = ['bitcoin','litecoin','dogecoin','dashpay','bitcoin_testnet','litecoin_testnet','dogecoin_testnet','dashpay_testnet']
PROTOCOL_VERSION    = {'bitcoin': 70001,'litecoin': 70002,'dogecoin':70003, 
                        'dashpay':70076,
                        'bitcoin_testnet':70001,'litecoin_testnet':70002,
                        'dogecoin_testnet':70003,'dashpay_testnet':70076}
MSG_MAGIC_BYTES     = {'bitcoin':'\xf9\xbe\xb4\xd9','litecoin':'\xfb\xc0\xb6\xdb',
                       'dogecoin':'\xc0\xc0\xc0\xc0','bitcoin_testnet':'\xfa\xbf\xb5\xda',
                       'litecoin_testnet':'\xfc\xc1\xb7\xdc',
                       'dogecoin_testnet':'\xfc\xc1\xb7\xdc',
                       'dashpay':'\xbf\x0c\x6b\xbd', 'dashpay_testnet':'\xce\xe2\xca\xff'} 
PORT                = {'bitcoin':8333,'litecoin':9333,'dogecoin':22556,'dashpay':9999,
                       'bitcoin_testnet':18333 ,'litecoin_testnet':19333,
                       'dogecoin_testnet':44556,'dashpay_testnet':19999}
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

                       # from chainparams.cpp / dashpay source
                       'dashpay': ["dnsseed.darkcoin.io","dnsseed.darkcoin.qo",
                                   "dnsseed.masternode.io","dnsseed.dashpay.io"],
                         
                       'bitcoin_testnet':["testnet-seed.alexykot.me",
                                          "testnet-seed.bitcoin.petertodd.org",
                                          "testnet-seed.bluematt.me",
                                          "testnet-seed.bitcoin.schildbach.de"],

                       'litecoin_testnet':["testnet-seed.litecointools.com",
                                           "testnet-seed.ltc.xurious.com", 
                                           "dnsseed.wemine-testnet.com"],

                       'dogecoin_testnet':["testdoge.lionservers.de", 
                                           "testdoge-seed.lionservers.de"], 
                       'dashpay_testnet':["testnet-seed.darkcoin.io","testnet-seed.darkcoin.qo",
                                          "test.dnsseed.masternode.io"]  
                      }
 



# used in PeerSocketsHandler to listen for message
MESSAGING_PORT      = {'bitcoin':1944,'litecoin':1945,'dogecoin':1946,'dashpay':1921,
                       'bitcoin_testnet':1947,'litecoin_testnet':1948,'dogecoin_testnet':1949,
                       'dashpay_testnet':1931}



