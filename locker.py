import tarfile
import base64
import os
import shutil
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import InvalidToken


class Locker:
    compression_ext = '.tar.gz'
    salt = b'\xab@r\x8a\\\xbb\xff\xde\xbf\xb3\x816\xe9\xf2\xf4C'

    def __init__(self, file_name, password):
        self.file_name = file_name
        self.password = password

    @property
    def key(self):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(self.password.encode()))

    def compress(self):
        print("Compressing {}...".format(self.file_name))
        with tarfile.open(self.file_name + self.compression_ext, 'w:gz') as o:
            o.add(self.file_name)

    def extract(self):
        with tarfile.open(self.file_name + self.compression_ext, 'r:gz') as i:
            i.extractall()


class Encryptor(Locker):
    def __init__(self, file_name, password):
        super().__init__(file_name, password)

    def encrypt(self):
        self.compress()
        print('Encrypting {}...'.format(self.file_name))

        if os.path.isdir(self.file_name):
            shutil.rmtree(self.file_name)
        else:
            os.remove(self.file_name)

        f = Fernet(self.key)
        with open(self.file_name + self.compression_ext, 'rb') as i:
            with open(self.file_name, 'wb') as o:
                o.write(f.encrypt(i.read()))

        os.remove(self.file_name + self.compression_ext)


class Decryptor(Locker):
    def __init__(self, file_name, password):
        super().__init__(file_name, password)

    def decrypt(self):
        print('Decrypting {}...'.format(self.file_name))

        f = Fernet(self.key)
        with open(self.file_name, 'rb') as i:
            with open(self.file_name + self.compression_ext, 'wb') as o:
                try:
                    o.write(f.decrypt(i.read()))
                    self.extract()
                except InvalidToken:
                    print('Wrong password')
                finally:
                    os.remove(self.file_name + self.compression_ext)
