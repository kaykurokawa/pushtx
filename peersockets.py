import logging 
import struct 
import socket
import select
import time
from hashlib import sha256

import protocol
import cryptoconfig

USER_AGENT='/Satoshi:0.10.0/' #BIP 14
TCP_RECV_PACKET_SIZE=4096
SOCKET_BLOCK_SECONDS=0 # None means blocking calls, 0 means non blocking calls
ADDRESS_TO_GET_IP='google.com' #connect to this address, in order to retreive computer IP
NONCE = 1 
DEFAULT_MAX_PEERS = 128 #max number of peers 
DEFAULT_NUM_TX_BROADCASTS = 20 #number of peers to broadcast tx to 
LOG_FILENAME='peersockets.log' 

def socketrecv(conn,init_buffer_size):
    msg=conn.recv(init_buffer_size)
    # None will be received when socket is closed
    if len(msg) == 0:
        return None
    expected_msg_len=struct.unpack('<H',msg[0:2])[0] #length of message in bytes,including this message length byte
    if len(msg) < expected_msg_len:
        while 1:
            new_msg=conn.recv(expected_msg_len-len(msg))
            msg+=new_msg
            if len(msg) == expected_msg_len:
                break                                
    return msg[2:]

def socketsend(conn,msg):
    if len(msg) > 65536:
        raise Exception('message length must be less than 16 bits')
    msg_len=len(msg)+2

    send_msg=struct.pack('<H',msg_len)+msg
    conn.sendall(send_msg)


# Handle multiple peer sockets
class PeerSocketsHandler(object):
    
    # tx_broadcast_list is a list of transactions to be broadcast 
    # in hex string (i.e, '03afb8..')
    def __init__(self,crypto,tx_broadcast_list=[],peer_list=[],
                    connect_to_dns_seeds = True, 
                    max_peers = DEFAULT_MAX_PEERS,
                    num_tx_broadcasts = DEFAULT_NUM_TX_BROADCASTS):

        if crypto not in cryptoconfig.SUPPORTED_CRYPTOS:
            raise Exception("Unsupported crypto {}".format(crypto))
 
        logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO,
            format="%(asctime)s; %(levelname)s; %(message)s")

        self.crypto=crypto
        self.max_peers=DEFAULT_MAX_PEERS
        self.num_tx_broadcasts=DEFAULT_NUM_TX_BROADCASTS

        self.my_ip  = self._get_my_ip()
        self.poller = select.poll()
        self.fileno_to_peer_dict    = {}
        self.address_to_peer_dict   = {}
        self.tx_broadcast_list      = []
        for tx in tx_broadcast_list: 
            self.tx_broadcast_list.append((tx,0))

        # setup messaging socket 
        self.msg_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.msg_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.msg_socket.bind(('localhost',cryptoconfig.MESSAGING_PORT[self.crypto]))
        self.msg_socket.listen(5)
        self.msg_socket.settimeout(0) # non blocking
        self.msg_recv_buffer=''

        # connect to DNS seeds
        if connect_to_dns_seeds:
            for address in cryptoconfig.DNS_SEEDS[self.crypto]:
                self.create_peer_socket(address)

        # connect to specified peers
        for address in peer_list:
            self.create_peer_socket(address)

    # function to get my current ip, 
    def _get_my_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((ADDRESS_TO_GET_IP,80))
        out= s.getsockname()[0]
        s.close()
        return out

    #create new peer socket at address
    def create_peer_socket(self,address):
        # check if address is domain name and convert it to TCP IP address
        if any([ c.isalpha() for c in address]):
            try:
                address=socket.gethostbyname(address)         
            except Exception as e:
                logging.warn("failed to resolve address "+address)
                return False 
        try:
            peer=PeerSocket(self.crypto)
            peer.connect(address)
        except IOError as e:
            logging.warn("I/O error({0}): {1}, could not connect to {}".format(e.errno, e.strerror,address))
            return False  
        self.fileno_to_peer_dict[peer.get_socket().fileno()]=peer 
        self.address_to_peer_dict[address]=peer
        eventmask=select.POLLIN|select.POLLPRI|select.POLLOUT|select.POLLERR|select.POLLHUP|select.POLLNVAL
        self.poller.register( peer.get_socket().fileno(),eventmask)
        return True 
      
    def remove_peer_socket(self,peer):
        #unregister and remove from dictionary 
        fileno=peer.get_socket().fileno()
        address=peer.get_address()
        self.poller.unregister(fileno)
        del self.fileno_to_peer_dict[fileno]
        del self.address_to_peer_dict[address]

    def get_num_peers(self):
        return len(self.fileno_to_peer_dict)

    def get_num_active_peers(self):
        out=0
        for peer in self.fileno_to_peer_dict.values():
            if peer.get_is_active():
                out+=1
        return out

    def add_new_broadcast_tx(self,tx):
        self.tx_broadcast_list.append((tx,0)) 

    def _recv_msg(self):
        try:
            conn,addr=self.msg_socket.accept()
            msg=socketrecv(conn,TCP_RECV_PACKET_SIZE)
        except Exception as e:
            msg=None
            
        if msg==None:
            return False
        msg_list=msg.split()

        if msg_list[0] == 'tx':
            self.add_new_broadcast_tx(msg_list[1])
            socketsend(conn,'ack')
            return True
        else:
            return False
    # poll peer sockets and do stuff if there is data
    def run(self): 

        # process any messages
        result=self._recv_msg()

        #broadcast tx 
        active_peer_list=[peer for peer in self.fileno_to_peer_dict.values() if peer.get_is_active()]
        for current_peer in active_peer_list:
            for (i,(tx,num_broadcasts)) in enumerate(self.tx_broadcast_list):
                was_broadcast=current_peer.broadcast(tx)# this will not broadcast more than once
                if was_broadcast:
                    logging.info("Tx has been broadcast: {}".format(tx))
                    self.tx_broadcast_list[i]=(tx,num_broadcasts+1)

        # remove tx after we broadcast NUM_TX_BROADCASTS times
        self.tx_broadcast_list=[x for x in self.tx_broadcast_list if x[1] < self.num_tx_broadcasts]
        
        # check received packets
        events=self.poller.poll()
        for event in events:
            poll_result=event[1]
            fileno=event[0]
            current_peer=self.fileno_to_peer_dict[fileno]
            if(poll_result & select.POLLOUT): #ready for write (means socket is connected)
                #don't check for POLLOUT anymore, since we know it is connected 
                self.poller.modify(fileno,
                    select.POLLIN|select.POLLPRI|select.POLLERR|select.POLLHUP|select.POLLNVAL) 
                # initialize by sending version 
                if not current_peer.get_is_active():
                    logging.info("connection established to {}".format(current_peer.address))
                    current_peer.send_version(self.my_ip)
                    current_peer.send_getaddr()
                    current_peer.set_is_active(True)
                    logging.info("num active peers: {}".format(self.get_num_active_peers()))

            if(poll_result & select.POLLIN):#ready for read( packet is available)
                current_peer.recv()
            
                #check new addresses we got from the peer and try to connect 
                while len(current_peer.peer_address_list) > 0 :
                    address=current_peer.peer_address_list.pop()
                    if address not in self.address_to_peer_dict:
                        if self.get_num_peers() < self.max_peers: 
                            self.create_peer_socket(address)
                #check new tx and add to db, Currently this does nothing  
                while len(current_peer.tx_hash_list) > 0 :
                    tx_hash=current_peer.tx_hash_list.pop()

            if(poll_result & select.POLLPRI): #urgent data to read
                pass
            if(poll_result & select.POLLERR): #Error condition
                logging.info("Error condition detected on {}".format(current_peer.get_address()))
            if(poll_result & select.POLLHUP): #hung up
                logging.info("Hung up detected on {}".format(current_peer.get_address()))
                self.remove_peer_socket(current_peer)
            if(poll_result & select.POLLNVAL): #invalid request, unopen descriptor
                logging.info("Invalid request detected on {}".format(current_peer.get_address()))
                self.remove_peer_socket(current_peer)

class PeerSocket(object):
    
    def __init__(self,crypto):
        self.crypto=crypto 
        self.port = cryptoconfig.PORT[crypto] 
        self.protocol_version=cryptoconfig.PROTOCOL_VERSION[crypto]
        self.msg_magic_bytes=cryptoconfig.MSG_MAGIC_BYTES[crypto]

        self.is_active=False
        self.address=''
        self.peer_address_list=[]
        self.tx_hash_list=[] #list of received tx hashes
        #dictionary where key is hash of tx we want to broadcast and value is tx
        #only contains tx's that have been broacast already using broadcast() function 
        self.broadcast_tx_dict={} 
        self.recv_buffer=''
        self.expected_msg_size=0
        self.version=''
        self.total_valid_bytes_received=0 
        self.total_junk_bytes_received=0

        # time of connection
        self.connection_time=None 

    def __del__(self):
        self.my_socket.close()

    def set_is_active(self,truefalse):
        self.is_active=truefalse
        if truefalse:
            self.connection_time = time.time()


    def get_address(self):
        return self.address

    def connect(self,address):
        self.address=address
        if('.' in address):
            socket_type=socket.AF_INET
        elif(':' in address):
            socket_type=socket.AF_INET6
        else:
            raise Exception("Unexpected address: "+address)
        self.my_socket=socket.socket(socket_type, socket.SOCK_STREAM)
        self.my_socket.settimeout(SOCKET_BLOCK_SECONDS)
        try:
            if(socket_type==socket.AF_INET): 
                self.my_socket.connect((address,self.port)) 
            else:
                self.my_socket.connect((address,self.port,0,0))
        except IOError as e:
            # 115 == Operation now in progress EINPROGRESS, this is expected
            if e.errno !=115: 
                return False
        return True 

    def get_socket(self):
        return self.my_socket
  
    def get_packet(self):

        if( len(self.recv_buffer) >= protocol.MSGHEADER_SIZE):
            data_length=protocol.get_length_msgheader(self.recv_buffer)
            self.expected_msg_size=data_length+protocol.MSGHEADER_SIZE
            #if valid command is not contained, packet will be thrown out 
            if protocol.is_valid_command(self.recv_buffer,self.crypto)==False:
                self.total_junk_bytes_received+=len(self.recv_buffer)
                self.expected_msg_size=0
                cmd = protocol.get_command_msgheader(self.recv_buffer)
                self.recv_buffer=''
                logging.error('Invalid command found in buffer: {}'.format(cmd))
                return '' 
        try:
            self.recv_buffer+=self.my_socket.recv(TCP_RECV_PACKET_SIZE)
        except IOError as e:
            logging.warn("Get packet from {0} I/O error({1}): {2}".format(self.address,e.errno, e.strerror))
            return ''  

        #if entire message is assembled exactly, return it
        if(len(self.recv_buffer) >= self.expected_msg_size and self.expected_msg_size !=0):
            self.total_valid_bytes_received+=self.expected_msg_size
            out=self.recv_buffer[0:self.expected_msg_size]
            self.recv_buffer=self.recv_buffer[self.expected_msg_size:]
            self.expected_msg_size=0            
            return out 
            
        #otherwise output is not ready, return empty string
        else:
            return '' 
           
    def get_is_active(self):
        return self.is_active 

    #send a ping pong to verify connection
    def verify_connection(self):
        data = struct.pack('<Q',NONCE)
        self._send_packet('ping',data)
        data=self.my_socket.recv(TCP_RECV_PACKET_SIZE)
        
        return process_pong(data)

    def _send_packet(self,command, payload):
        lc = len(command)
        assert (lc < 12)
        cmd = command + ('\x00' * (12 - lc))
        h = protocol.dhash (payload)
        checksum, = struct.unpack ('<I', h[:4])
        packet = struct.pack ('<4s12sII',
            self.msg_magic_bytes,cmd,len(payload),checksum) + payload
        try:
            self.my_socket.send(packet)
        except IOError as e:
            logging.warn("Send packet to {0} I/O error({1}): {2}".format(self.address,e.errno, e.strerror))
            return False
        return True

    def send_version(self,my_ip):
        data = struct.pack ('<IQQ', self.protocol_version, 1, int(time.time()))
        data += protocol.pack_net_addr ((1, (my_ip, self.port)))
        data += protocol.pack_net_addr ((1, (self.address, self.port)))
        data += struct.pack ('<Q',NONCE)
        data += protocol.pack_var_str (USER_AGENT)
        start_height = 0
        #ignore bip37 for now - leave True
        data += struct.pack ('<IB', start_height, 1)
        self._send_packet ('version', data)

    # unused
    def send_getaddr(self):
        data = struct.pack('0c')
        self._send_packet('getaddr',data)   


    def _send_tx(self,tx_hash):
        # send only if we have tx_hash 
        if tx_hash in self.broadcast_tx_dict:
            data=self.broadcast_tx_dict[tx_hash]
            self._send_packet('tx',data)
       
    def recv(self):
        data=self.get_packet()
        if(len(data)!=0):
            self.process_data(data)
            return True
        else:
            return False

    # Return True, if broadcast succeeds, False oterwise.  
    # Unique tx can only be broadcast once, attempts to broadcast
    # identical tx will return False. 
    # tx is expected to be a hex string, i.e. '02aba8...'
    def broadcast(self,tx):
        tx=tx.decode('hex')
        tx_hash=protocol.dhash(tx) #need to hash here
        # we only broadcast if tx is new 
        if tx_hash not in self.broadcast_tx_dict:
            self.broadcast_tx_dict[tx_hash]=tx
            data =  protocol.pack_var_int(1) 
            data += struct.pack('<I32s',1,tx_hash) #MSG_TX
            self._send_packet('inv',data)
            return True
            # we will receive getdata (make sure we have hash) 
            # and process_data will call _send_tx when inv message 
            # received 
        return False

    def process_data(self,data):
        if protocol.compare_command(data,"getaddr"): #get known peers
            pass
        elif protocol.compare_command(data,"addr"):#in reponse to getaddr
            self._process_addr(data)
        elif protocol.compare_command(data,"version"):
            pass
        elif protocol.compare_command(data,"verack"):
            pass
        elif protocol.compare_command(data,"inv"): #advertise knowledge of tx or block
            self._process_inv(data)
        elif protocol.compare_command(data,"getblocks"):#request an inv packet for blocks
            pass
        elif protocol.compare_command(data,"getheaders"):#request headers
            pass
        elif protocol.compare_command(data,"headers"):#return header in reponse to getheader
            pass
        elif protocol.compare_command(data,"getdata"):#get data from peer after broadcasting tx via inv
            self._process_get_data(data)  
        elif protocol.compare_command(data,"notfound"):#not found is sent after getdata recieved
            pass
        elif protocol.compare_command(data,"block"):#describe a block in reponse to getdata
            pass
        elif protocol.compare_command(data,"tx"):#describe a transaction in repones to getdata
            pass
        elif protocol.compare_command(data,"pong"):#response to ping
            pass
        elif protocol.compare_command(data,"ping"):#query if tcp ip is alive
            pass
        elif protocol.compare_command(data,"reject"): 
            self._process_reject(data)
        elif (self.crypto in ['dashpay','dashpay_testnet'] and 
              protocol.compare_command(data,'dseep')):
            pass
        else:
            logging.warn("unhandled command recieved:{}".format(
                                    protocol.get_command_msgheader(data)))

    def _process_reject(self,data):
        payload = protocol.get_payload(data)
        varint_tuple = protocol.read_var_int(payload)

        size_message = varint_tuple[0]
        varint_size = varint_tuple[1]
        message_rejected = payload[varint_size:varint_size+size_message]
        code = struct.unpack('B',payload[varint_size+size_message:varint_size+size_message+1])[0]
        
        payload = payload[varint_size+size_message+1:]

        varint_tuple = protocol.read_var_int(payload)
        size_reason = varint_tuple[0]
        varint_size=varint_tuple[1]
        reason = payload[varint_size:varint_size+size_reason]
        data = payload[varint_size+size_reason:]

        if message_rejected == 'tx':
            pass

        msg='{} rejected, reason: {}, code: {}, data: {}'.format(message_rejected,reason,code,data)
        logging.error(msg)      


    def _process_get_data(self,data):
        payload         =   protocol.get_payload(data)
        varint_tuple    =   protocol.read_var_int(payload)
        num_invs        =   varint_tuple[0]
        varint_size     =   varint_tuple[1]
        inv_data        =   payload[varint_size:]         
        for i in range(0,num_invs):
            begin_index=i*36
            end_index=begin_index+36
            inv_type = struct.unpack('<I',inv_data[begin_index:begin_index+4])[0]
            inv_hash = struct.unpack('32c',inv_data[begin_index+4:begin_index+36])
            if(inv_type ==0):#error
                pass
            elif(inv_type==1):#tx
                tx_hash=''.join(inv_hash) #convert tuple to string
                self._send_tx(tx_hash)
            elif(inv_type==2):#block
                pass 
            else:
                logging.error("unknown inv {} found".format(inv_type))

    def _process_addr(self,data):
        payload         =   protocol.get_payload(data)
        varint_tuple    =   protocol.read_var_int(payload)
        num_ips         =   varint_tuple[0]
        varint_size     =   varint_tuple[1]
        ip_data         =   payload[varint_size:] 
        for i in range(0,num_ips):
            begin_index=i*30
            end_index=begin_index+30
            timestamp = struct.unpack('<I',ip_data[begin_index:begin_index+4])[0]
            services = struct.unpack('<Q',ip_data[begin_index+4:begin_index+12])[0]
            ipv6= struct.unpack('16c',ip_data[begin_index+12:begin_index+28])[0]
            ipv4= struct.unpack('4c',ip_data[begin_index+24:begin_index+28])[0]
            port=struct.unpack('!H',ip_data[begin_index+28:begin_index+30])[0]
            self.peer_address_list.append(socket.inet_ntop(socket.AF_INET,ip_data[begin_index+24:begin_index+28])) 

    def _process_inv(self,data):
        payload         =   protocol.get_payload(data)
        varint_tuple    =   protocol.read_var_int(payload)
        num_invs        =   varint_tuple[0]
        varint_size     =   varint_tuple[1]
        inv_data        =   payload[varint_size:]
        for i in range(0,num_invs):
            begin_index=i*36
            end_index=begin_index+36
            inv_type = struct.unpack('<I',inv_data[begin_index:begin_index+4])[0]
            inv_hash = struct.unpack('32c',inv_data[begin_index+4:begin_index+36])
            if not protocol.is_valid_inv_type(inv_type,self.crypto):
                logging.error("unknown inv {} found".format(inv_type))
            if inv_type == 1:#tx
                self._process_inv_tx(inv_hash)
            elif inv_type == 2:#block
                self._process_inv_block(inv_hash)
            elif inv_type == 3:#filtered block
                pass

    def _process_inv_tx(self,inv_hash):
        self.tx_hash_list.append(inv_hash)

    def _process_inv_block(self,inv_hash):
        pass

    def _process_pong(data):
        if(protocol.compare_command(data,"pong")):
            return True
        else:
            return False 

    def _process_version_handshake(socket):
        data=socket.recv(1024)
        if(protocol.compare_command(data,"version")):
            logging.info("version message recieved")
        else:
            logging.error("unexpected message recieved in version handshake")
        data=socket.recv(1024)
        out_tuple=struct.unpack('<I12c',data[0:16]) 
        if(protocol.compare_command(data,"verack")):
            logging.info("verack message recieved")
        else: 
            logging.info("message type:",out_tuple[1:])


