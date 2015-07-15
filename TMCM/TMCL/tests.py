#!/usr/bin/env python

import unittest
import codec

import random as rnd


MAXITER = 200
REQUEST_KEYS = codec.REQUEST_KEYS + ['value']
REPLY_KEYS   = codec.REPLY_KEYS   + ['value']



class CodecTestCase(unittest.TestCase):


    def _gen_byte(self, min_i=0, max_i=256):
        return rnd.randint(min_i, max_i-1)

    def _gen_bytes(self, length=5):
        return [self._gen_byte() for _ in xrange(length)]

    def _gen_pos_bytes(self, length=5):
        return [self._gen_byte(max_i=128)] + self._gen_bytes(length-1)

    def _gen_neg_bytes(self, length=5):
        return [self._gen_byte(min_i=128)] + self._gen_bytes(length-1)

    def _gen_number(self, length=None):
        if length is None:
            length = rnd.randint(1, 9)
        value = [rnd.randint(0, 9) for _ in xrange(length)]
        value = (str(s) for s in value)
        value = "".join(value)
        return int(value)

    def _gen_cmd_string(self, length=8):
        values = [rnd.randint(0, 9) for _ in xrange(length)]
        chksum = sum(values)
        values.append(chksum)
        string = "".join(chr(v) for v in values)
        return string


    def test_bit_operations(self):
        for i in xrange(128):
            i_s = codec.set_sign_bit(i)
            i_c = codec.clear_sign_bit(i_s)

            self.assertEqual(i, i_c)
            self.assertEqual(i + 128, i_s)

            self.assertFalse(codec.is_sign_bit_set(i))
            self.assertTrue(codec.is_sign_bit_set(i_s))
            self.assertFalse(codec.is_sign_bit_set(i_c))

        for i in xrange(128, 256):
            i_c = codec.clear_sign_bit(i)
            i_s = codec.set_sign_bit(i_c)

            self.assertEqual(i, i_s)
            self.assertEqual(i - 128, i_c)

            self.assertTrue(codec.is_sign_bit_set(i))
            self.assertFalse(codec.is_sign_bit_set(i_c))
            self.assertTrue(codec.is_sign_bit_set(i_s))


    def test_byte(self):
        for i in xrange(MAXITER):
            self.assertIn(codec.byte(i), range(256))


    def test_checksum(self):
        for i in xrange(MAXITER):
            self.assertEqual(codec.checksum(i*[i]), codec.byte(i*i))



    def test_encodeBytes(self):
        value = 123456789

        bytes = codec.encodeBytes(value)
        self.assertEqual([7, 91, 205, 21], bytes)

        new_value = codec.decodeBytes(bytes)
        self.assertEqual(value, new_value)


    def test_decodeBytes(self):
        bytes = [1, 2, 3, 4]

        value = codec.decodeBytes(bytes)
        self.assertEqual(16909060, value)

        new_bytes = codec.encodeBytes(value)
        self.assertEqual(bytes, new_bytes)


    def test_encdecBytes(self):
        for _ in xrange(MAXITER):
            value = self._gen_number()
            bytes = codec.encodeBytes(value)
            new_value = codec.decodeBytes(bytes)

            self.assertEqual(value, new_value)


    def test_decencBytes(self):
        for _ in xrange(MAXITER):
            bytes = self._gen_bytes(length=4)
            value = codec.decodeBytes(bytes)
            new_bytes = codec.encodeBytes(value)

            self.assertEqual(bytes, new_bytes)


    def test_decencNegBytes(self):
        for _ in xrange(MAXITER):
            bytes = self._gen_neg_bytes(length=4)
            value = codec.decodeBytes(bytes)
            new_bytes = codec.encodeBytes(value)

            self.assertEqual(bytes, new_bytes)


    def test_decencPosBytes(self):
        for _ in xrange(MAXITER):
            bytes = self._gen_pos_bytes(length=4)
            value = codec.decodeBytes(bytes)
            new_bytes = codec.encodeBytes(value)

            self.assertEqual(bytes, new_bytes)



    def _help_test_encodeReAllCommand(self, encoder, decoder, keys):
        string = "ABCD\x00\x00\x00EO"
        values = [ord(s) for s in string]

        result = encoder(values[0], values[1], values[2], values[3], sum(values[4:8]))
        self.assertEqual(string, result)


    def _help_test_decodeReAllCommand(self, encoder, decoder, keys):
        string = "ABCD\x00\x00\x00EO"
        result = decoder(string)

        for i, k in enumerate(keys[:4]):
            self.assertEqual(ord(string[i]), result[k])

        values = sum(ord(s) for s in string[4:8])
        self.assertEqual(values, result['value'])

        self.assertEqual(ord(string[7]), result['value'])
        self.assertEqual(ord(string[8]), result['checksum'])


    def test_encodeRequestCommand(self):
        self._help_test_encodeReAllCommand(codec.encodeRequestCommand, codec.decodeRequestCommand, REQUEST_KEYS)

    def test_decodeRequestCommand(self):
        self._help_test_decodeReAllCommand(codec.encodeRequestCommand, codec.decodeRequestCommand, REQUEST_KEYS)

    def test_encodeReplyCommand(self):
        self._help_test_encodeReAllCommand(codec.encodeReplyCommand, codec.decodeReplyCommand, REPLY_KEYS)

    def test_decodeReplyCommand(self):
        self._help_test_decodeReAllCommand(codec.encodeReplyCommand, codec.decodeReplyCommand, REPLY_KEYS)



    def _help_test_encdecReAllCommand(self, encoder, decoder, keys):
        for _ in xrange(MAXITER):
            values = self._gen_bytes(length=len(keys))
            string = encoder(*values)
            result = decoder(string)

            for i, k in enumerate(keys):
                self.assertEqual(values[i], result[k])

            self.assertEqual(sum(values) % 256, result['checksum'])


    def _help_test_decencReALLCommand(self, encoder, decoder, keys):
        for _ in xrange(MAXITER):
            string = self._gen_cmd_string()
            values = decoder(string)

            unpacked = (values[k] for k in keys)
            new_string = encoder(*unpacked)

            self.assertEqual(string, new_string)


    def test_encdecRequestCommand(self):
        self._help_test_encdecReAllCommand(codec.encodeRequestCommand, codec.decodeRequestCommand, REQUEST_KEYS)

    def test_decencRequestCommand(self):
        self._help_test_decencReALLCommand(codec.encodeRequestCommand, codec.decodeRequestCommand, REQUEST_KEYS)


    def test_encdecReplyCommand(self):
        self._help_test_encdecReAllCommand(codec.encodeReplyCommand, codec.decodeReplyCommand, REPLY_KEYS)

    def test_decencReplyCommand(self):
        self._help_test_decencReALLCommand(codec.encodeReplyCommand, codec.decodeReplyCommand, REPLY_KEYS)



    def test_encodeCommand(self):
        string = "ABCD\x00\x00\x00EO"
        params = [ord(s) for s in string[:4]]
        values = ord(string[7])
#        values = sum(ord(s) for s in string[4:8])

        new_string = codec.encodeCommand(params, values)
        self.assertEqual(string, new_string)


    def test_decodeCommand(self):
        keys = range(4)
        string = "ABCD\x00\x00\x00EO"

        result = codec.decodeCommand(string, keys)

        for i, k in enumerate(keys):
            self.assertEqual(ord(string[i]), result[k])

        values = sum(ord(s) for s in string[4:8])
        self.assertEqual(values, result['value'])

        self.assertEqual(ord(string[7]), result['value'])
        self.assertEqual(ord(string[8]), result['checksum'])


    def test_encdecCommand(self):
        keys = range(4)
        for _ in xrange(MAXITER):
            params = self._gen_bytes(length=4)
            values = self._gen_byte()
            chksum = sum(params, values) % 256

            string = codec.encodeCommand(params, values)
            result = codec.decodeCommand(string, keys)

            for i, k in enumerate(keys):
                self.assertEqual(params[i], result[k])

            self.assertEqual(values, result['value'])
            self.assertEqual(chksum, result['checksum'])


    def test_decencCommand(self):
        keys = range(4)
        for _ in xrange(MAXITER):
            string = self._gen_cmd_string()

            decoded = codec.decodeCommand(string, keys)
            params = [decoded[k] for k in keys]
            values = decoded['value']
            new_string = codec.encodeCommand(params, values)

            self.assertEqual(string[:4],  new_string[:4])  # parameter part
            self.assertEqual(string[4:8], new_string[4:8]) # value part
            self.assertEqual(string[8],   new_string[8])   # checksum part
            self.assertEqual(string,      new_string)






if __name__ == '__main__':
    unittest.main()


