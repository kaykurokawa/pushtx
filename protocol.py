# Contains function to process bitcoin messages 
# Some of the code her is taken from Caesure by Sam Rushing (https://github.com/samrushing/caesure)

import socket
import struct
from hashlib import sha256

VALID_COMMANDS=['getaddr','addr','inv','getblocks','headers','getheaders','getdata','notfound','block','tx','pong',
                'ping','version','verack','reject']

MSGHEADER_SIZE=24
def is_valid_command(data):    
    out = any([compare_command(data,command) for command in VALID_COMMANDS])
    return out

def compare_command(data, string):  
    tuple_start=get_command_msgheader(data)
    for index,char in enumerate(string):
        if( tuple_start[index]!=char):
            return False        
    return True

def get_command_msgheader(data):
    return struct.unpack('12c',data[4:16])

def get_magic_msgheader(data):
    return struct.unpack('<I',data[0:4])[0]

def get_length_msgheader(data):
    if(len(data)<20):
      raise Exception("data must be of length 20 at least, length is:%d"%len(data))
    return struct.unpack('<I',data[16:20])[0]

def get_checksum_msgheader(data):
    return struct.unpack('<I',data[20:24])[0]

def get_payload(data):
    return data[24:] 

def dhash (s):
    return sha256(sha256(s).digest()).digest()

def pack_net_addr ((services, (addr, port))):
    addr = pack_ip_addr (addr)
    port = struct.pack ('!H', port)
    return struct.pack ('<Q', services) + addr + port

def pack_ip_addr (addr):
    # only v4 right now
    # XXX this is probably no longer true, the dns seeds are returning v6 addrs
    return socket.inet_pton (socket.AF_INET6, '::ffff:%s' % (addr,))

def pack_var_str (s):
    return pack_var_int (len (s)) + s


def pack_var_int (n):
    if n < 0xfd:
        return chr(n)
    elif n < 1<<16:
        return '\xfd' + struct.pack ('<H', n)
    elif n < 1<<32:
        return '\xfe' + struct.pack ('<I', n)
    else:
        return '\xff' + struct.pack ('<Q', n)

#return tuple with the integer and size of varint object
def read_var_int(data):
    b1=struct.unpack('<B',data[0])
    b1=b1[0]
    if(b1<0xfd):
        return (b1,1)
    elif(b1==0xfd):
        b2=struct.unpack('<H',data[1:3])
        return(b2[0],3)
    elif(b1==0xfe):
        b3=struct.unpack('<I',data[1:5])
        return(b3[0],5)
    elif(b1==0xff): #b1==0xff
        b4=struct.unpack('<Q',data[1:9])
        return(b4[0],9)
    else:
        raise Exception("varint read failed") 


