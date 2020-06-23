from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os


class TransportKey:
    '''
    initial key
    '''
    def __init__(self):
        if not os.path.isdir("key"):
            os.mkdir("key")
        if os.path.exists('key/transport.pem') and os.path.exists('key/transport.pub'):
            with open('key/transport.pem', 'rb') as pem_in:
                pemlines = pem_in.read()
            private_pem = serialization.load_pem_private_key(pemlines, None, default_backend())

            with open('key/transport.pub', 'rb') as pem_in:
                publines = pem_in.read()
            public_pem = serialization.load_pem_public_key(publines, default_backend())

        else:

            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=1024,
                backend=default_backend()
            )
            public_key = private_key.public_key()

            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )

            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            if not os.path.exists('key/transport.pem'):
                with open('key/transport.pem', 'wb') as pem_out:
                    pem_out.write(private_pem)

            if not os.path.exists('key/transport.pub'):
                with open('key/transport.pub', 'wb') as pub_out:
                    pub_out.write(public_pem)
        # print(public_pem)
        # print(private_pem)

        self.privateKey = private_pem
        self.publicKey = public_pem


