
from collections import OrderedDict

from error import *


SIGN_BIT = 7
COMMAND_STRING_LENGTH = 9
REQUEST_KEYS = ['module-address', 'command-number', 'type-number', 'motor-number']
REPLY_KEYS = ['reply-address', 'module-address', 'status', 'command-number']



def is_sign_bit_set(value, bit=SIGN_BIT):
    """Test if sign bit is set in value"""
    return value & (1<<bit) != 0

def set_sign_bit(value, bit=SIGN_BIT):
    """Set sign bit to 1 (negative) in value"""
    return value | (1<<bit)

def clear_sign_bit(value, bit=SIGN_BIT):
    """Set sign bit to 0 (positive) in value"""
    return value & ~(1<<bit)


def byte(n):
    """Convert n to byte in range(256)"""
    return int(n) % (1<<8)


def checksum(bytes):
    """Calculate checksum byte for given list of bytes"""
    return byte(sum(bytes))


def encodeBytes(value, max_i=3):
    """
    Encode a value to a byte list
    Sets the MSB for negative value
    """
    bytes = [byte(int(abs(value)) >> i*8) for i in range(max_i, -1, -1)]

    if value < 0:
        bytes[0] = set_sign_bit(bytes[0])

    return bytes


def decodeBytes(bytes, max_i=3):
    """
    Decode a byte list to a value
    Returns a negative value when MSB is set
    """
    # bytes is mutable, hence changes would alter the original, thus make a copy:
    bytes = list(bytes)

    sign = +1
    if is_sign_bit_set(bytes[0]):
        sign = -1
        bytes[0] = clear_sign_bit(bytes[0])

    return sign * sum(b << (max_i-i)*8 for i, b in enumerate(bytes))


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



