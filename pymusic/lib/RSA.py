import binascii

import rsa


class RSA(object):
    """RSA."""

    def __init__(self, n, e):
        super(RSA, self).__init__()
        n = int(n, 16)
        e = int(e, 16)
        self.key = rsa.PublicKey(n, e)

    def encrypt(self, message):
        result = rsa.encrypt(message.encode(), self.key)
        result = binascii.b2a_hex(result)
        return result.decode()
