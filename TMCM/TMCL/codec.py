
from error import *


def byte(n):
    """Convert n to byte in range(256)"""
    return int(n) % (1<<8)


def encodeRequestCommand(m_address, n_command, n_type, n_motor, value, debug=False):
    # convert to bytes
    m_address = byte(m_address)
    n_command = byte(n_command)
    n_type = byte(n_type)
    n_motor = byte(n_motor)
    value = [byte(int(value) >> i*8) for i in range(3,-1,-1)]
    # generate command
    checksum = byte(m_address + n_command + n_type + n_motor + sum(value))
    tmcl_bytes = [m_address, n_command, n_type, n_motor] + value + [checksum]
    tmcl_cmd = sum(b << (8-i)*8 for i,b in enumerate(tmcl_bytes))
    if debug:
        print "{0:0>18X}".format(tmcl_cmd), "".join([chr(b) for b in tmcl_bytes])
    return "".join([chr(b) for b in tmcl_bytes])

def encodeReplyCommand(r_address, m_address, status, n_command, value, debug=False):
    # convert to bytes
    r_address = byte(r_address)
    m_address = byte(m_address)
    status = byte(status)
    n_command = byte(n_command)
    value = [byte(int(value) >> i*8) for i in range(3,-1,-1)]
    # generate command
    checksum = byte(r_address + m_address + status + n_command + sum(value))
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


