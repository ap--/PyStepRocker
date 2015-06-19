
from error import *


def encodeRequestCommand(m_address, n_command, n_type, n_motor, value, debug=False):
    # convert to bytes
    m_address = int(m_address) % (1<<8)
    n_command = int(n_command) % (1<<8)
    n_type = int(n_type) % (1<<8)
    n_motor = int(n_motor) % (1<<8)
    value = [(int(value) >> i*8) % (1<<8) for i in range(3,-1,-1)]
    # generate command
    checksum = (m_address + n_command + n_type + n_motor + sum(value)) % (1<<8)
    tmcl_bytes = [m_address, n_command, n_type, n_motor] + value + [checksum]
    tmcl_cmd = sum(b << (8-i)*8 for i,b in enumerate(tmcl_bytes))
    if debug:
        print "{0:0>18X}".format(tmcl_cmd), "".join([chr(b) for b in tmcl_bytes])
    return "".join([chr(b) for b in tmcl_bytes])

def encodeReplyCommand(r_address, m_address, status, n_command, value, debug=False):
    # convert to bytes
    r_address = int(r_address) % (1<<8)
    m_address = int(m_address) % (1<<8)
    status = int(status) % (1<<8)
    n_command = int(n_command) % (1<<8)
    value = [(int(value) >> i*8) % (1<<8) for i in range(3,-1,-1)]
    # generate command
    checksum = (r_address + m_address + status + n_command + sum(value)) % (1<<8)
    tmcl_bytes = [r_address, m_address, status, n_command] + value + [checksum]
    tmcl_cmd = sum(b << (8-i)*8 for i,b in enumerate(tmcl_bytes))
    if debug:
        print "{0:0>18X}".format(tmcl_cmd), "".join([chr(b) for b in tmcl_bytes])
    return "".join([chr(b) for b in tmcl_bytes])

def decodeRequestCommand(cmd_string):
    byte_array = bytearray(cmd_string)
    if len(byte_array) != 9:
        raise TMCLError("Commandstring shorter than 9 bytes")
    if byte_array[8] != sum(byte_array[:8]) % (1<<8):
        raise TMCLError("Checksum error in command %s" % cmd_string)
    ret = {}
    ret['module-address'] = byte_array[0]
    ret['command-number'] = byte_array[1]
    ret['type-number'] = byte_array[2]
    ret['motor-number'] = byte_array[3]
    ret['value'] = sum(b << (3-i)*8 for i,b in enumerate(byte_array[4:8]))
    ret['checksum'] = byte_array[8]
    return ret    

def decodeReplyCommand(cmd_string):
    byte_array = bytearray(cmd_string)
    if len(byte_array) != 9:
        raise TMCLError("Commandstring shorter than 9 bytes")
    if byte_array[8] != sum(byte_array[:8]) % (1<<8):
        raise TMCLError("Checksum error in command %s" % cmd_string)
    ret = {}
    ret['reply-address'] = byte_array[0]
    ret['module-address'] = byte_array[1]
    ret['status'] = byte_array[2]
    ret['command-number'] = byte_array[3]
    ret['value'] = sum(b << (3-i)*8 for i,b in enumerate(byte_array[4:8]))
    ret['checksum'] = byte_array[8]
    return ret


