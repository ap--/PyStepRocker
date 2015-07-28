
from collections import OrderedDict

from error import *


COMMAND_STRING_LENGTH = 9
REQUEST_KEYS = ['module-address', 'command-number', 'type-number', 'motor-number']
REPLY_KEYS = ['reply-address', 'module-address', 'status', 'command-number']



def byte(n):
    """Convert n to byte in range(256)"""
    return int(n) % (1<<8)


def checksum(bytes):
    """Calculate checksum byte for given list of bytes"""
    return byte(sum(bytes))


def encodeBytes(value, max_i=3):
    """
    Encode a value to a byte list
    If value negative, shift above 2**31 by adding 2**32
    """
    if value < 0:
        value += (1<<32)

    return [byte(int(value) >> i*8) for i in range(max_i, -1, -1)]


def decodeBytes(bytes, max_i=3):
    """
    Decode a byte list to a value
    If value larger than allowed positive values (0 to 2**31), subtract 2**32
    """
    value = sum(b << (max_i-i)*8 for i, b in enumerate(bytes))

    if not value < (1<<31):
        value -= (1<<32)

    return value


def encodeRequestCommand(m_address, n_command, n_type, n_motor, value, debug=False):
    """Encode a request using encodeCommand"""
    return encodeCommand([m_address, n_command, n_type, n_motor], value, debug=debug)

def encodeReplyCommand(r_address, m_address, status, n_command, value, debug=False):
    """Encode a reply using encodeCommand"""
    return encodeCommand([r_address, m_address, status, n_command], value, debug=debug)


def encodeCommand(parameters, value, debug=False):
    """
    Encode a command string:
    Convert parameters and value to byte lists
    Calculate the checksum
    Join everything and convert to string
    """
    bytes = [byte(p) for p in parameters]
    value = encodeBytes(value)
    bytes += value
    chsum = checksum(bytes)
    bytes += [chsum]
    result = "".join([chr(b) for b in bytes])

    if debug:
        cmd = decodeBytes(bytes, max_i=8)
        print "{0:0>18X}".format(cmd), result
    return result



def decodeRequestCommand(cmd_string):
    """Decode a request using decodeCommand"""
    return decodeCommand(cmd_string, REQUEST_KEYS)

def decodeReplyCommand(cmd_string):
    """Decode a reply using decodeCommand"""
    return decodeCommand(cmd_string, REPLY_KEYS)


def decodeCommand(cmd_string, keys):
    """
    Decode a command string:
    Convert command string to byte list
    Do some checks on string length and checksum
    Fill dict with result according to keys
    """
    byte_array = bytearray(cmd_string)
    if len(byte_array) != COMMAND_STRING_LENGTH:
        raise TMCLError("Command-string length ({} bytes) does not equal {} bytes".format(len(byte_array), COMMAND_STRING_LENGTH))
    if byte_array[8] != checksum(byte_array[:8]):
        raise TMCLError("Checksum error in command {}: {} != {}".format(cmd_string, byte_array[8], checksum(byte_array[:8])))

    result = OrderedDict()
    for i, k in enumerate(keys):
        result[k] = byte_array[i]

    result['value'] = decodeBytes(byte_array[4:8])
    result['checksum'] = byte_array[8]

    return result



def hexString(cmd):
    """Convert encoded command string to human-readable string of hex values"""
    s = ['{:x}'.format(i).rjust(2) for i in list(bytearray(cmd))]
    return  "[" + ", ".join(s) + "]"



