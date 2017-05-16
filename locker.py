import base64
from os import walk, remove, cpu_count
from os.path import join, isdir
from multiprocessing import Pool
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import InvalidToken


class Locker:
    '''
    This is just a base class. You should not use this directly. Instead, use
    Encryptor or Decryptor class.
    '''
    encrypted_ext = '.dat'
    salt = b'\xab@r\x8a\\\xbb\xff\xde\xbf\xb3\x816\xe9\xf2\xf4C'

    def __init__(self, files, password):
        self.files = files
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

    @property
    def paths(self):
        files = self.files
        for file in files:
            if isdir(file):
                for dirpath, dirnames, filenames in walk(file):
                    for filename in filenames:
                        yield join(dirpath, filename)
            else:
                yield file


class Encryptor(Locker):
    '''
    'files': List of files which will be encrypted. 
    'password': A string.
    '''

    def __init__(self, files, password):
        super().__init__(files, password)

    def encrypt(self, path):
        '''
        Encrypt a single file.
        '''
        print('Encrypting {}...'.format(path))
        f = Fernet(self.key)
        try:
            with open(path, 'rb') as i:
                with open(path + self.encrypted_ext, 'wb') as o:
                    o.write(f.encrypt(i.read()))
                    remove(path)
        except FileNotFoundError:
            print('No such file or directory: {}'.format(path))

    def start(self):
        '''
        Using map which has 'encrypt' function as the function parameter to
        encrypt all the files.
        '''
        encrypt = self.encrypt
        paths = self.paths
        p = Pool(cpu_count())
        p.map(encrypt, paths)


class Decryptor(Locker):
    '''
    'files': List of files which will be decrypted. 
    'password': A string.
    '''

    def __init__(self, files, password):
        super().__init__(files, password)

    def decrypt(self, path):
        '''
        Decrypt a single file.
        '''
        print('Decrypting {}...'.format(path))
        if path.endswith(self.encrypted_ext):
            f = Fernet(self.key)
            try:
                with open(path, 'rb') as i:
                    with open(path.replace(self.encrypted_ext, ''), 'wb') as o:
                        try:
                            o.write(f.decrypt(i.read()))
                        except InvalidToken:
                            remove(path.replace(self.encrypted_ext, ''))
                            print('Incorrect password for {}'.format(path))
                        else:
                            remove(path)

            except FileNotFoundError:
                print('No such file or directory: {}'.format(path))
        else:
            print("{} is not an encrypted file".format(path))

    def start(self):
        '''
        Using map which has 'decrypt' function as the function parameter to
        decrypt all the files.
        '''
        decrypt = self.decrypt
        paths = self.paths
        p = Pool(cpu_count())
        p.map(decrypt, paths)
