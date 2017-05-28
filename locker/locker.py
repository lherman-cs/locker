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

    _encrypted_ext = '.dat'
    _salt = b'\xab@r\x8a\\\xbb\xff\xde\xbf\xb3\x816\xe9\xf2\xf4C'

    def __init__(self, files, password):
        '''
        creates the variables associated with the class

        :type files: list
        :param files: paths to be encrypted/decrypted

        :type password: string
        :param password: password to lock/unlock the files
        '''

        self._files = files
        self._password = password

    @property
    def _key(self):
        '''
        auto-generated key property
        '''

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(self._password.encode()))

    @property
    def _paths(self):
        '''
        recursively find all the paths from the given arguments
        '''

        files = self._files
        for file in files:
            if isdir(file):
                for dirpath, dirnames, filenames in walk(file):
                    for filename in filenames:
                        yield join(dirpath, filename)
            else:
                yield file


class Encryptor(Locker):
    '''
    Inherited from Locker. This class is spesifically used for
    encrypt the data.
    '''

    def __init__(self, files, password):
        '''
        creates the variables associated with the class

        :type files: list
        :param files: paths to be encrypted/decrypted

        :type password: string
        :param password: password to lock/unlock the files
        '''

        super().__init__(files, password)

    def _encrypt(self, path):
        '''
        encrypt a single file.

        :type path: string
        :param path: a path of a single file to be encrypted
        '''

        print('Encrypting {}...'.format(path))
        f = Fernet(self._key)
        try:
            with open(path, 'rb') as i:
                with open(path + self._encrypted_ext, 'wb') as o:
                    o.write(f.encrypt(i.read()))
                    remove(path)
        except FileNotFoundError:
            print('No such file or directory: {}'.format(path))

    def start(self):
        '''
        using map which has 'encrypt' function as the function parameter to
        encrypt all the _files.
        '''

        encrypt = self._encrypt
        paths = self._paths
        p = Pool(cpu_count())
        p.map(encrypt, paths)


class Decryptor(Locker):
    '''
    Inherited from Locker. This class is spesifically used for
    encrypt the data.
    '''

    def __init__(self, files, password):
        '''
        creates the variables associated with the class

        :type files: list
        :param files: paths to be encrypted/decrypted

        :type password: string
        :param password: password to lock/unlock the files
        '''

        super().__init__(files, password)

    def _decrypt(self, path):
        '''
        decrypt a single file.

        :type path: string
        :param path: a path of a single file to be decrypted
        '''

        print('Decrypting {}...'.format(path))
        if path.endswith(self._encrypted_ext):
            f = Fernet(self._key)
            try:
                with open(path, 'rb') as i:
                    with open(path.replace(self._encrypted_ext, ''), 'wb') as o:
                        try:
                            o.write(f.decrypt(i.read()))
                        except InvalidToken:
                            # Remove newly created file if the given password is
                            # incorrect

                            remove(path.replace(self._encrypted_ext, ''))
                            print('Incorrect _password for {}'.format(path))
                        else:
                            remove(path)

            except FileNotFoundError:
                print('No such file or directory: {}'.format(path))
        else:
            print("{} is not an encrypted file".format(path))

    def start(self):
        '''
        using map which has 'decrypt' function as the function parameter to
        decrypt all the _files.
        '''

        decrypt = self._decrypt
        paths = self._paths
        p = Pool(cpu_count())
        p.map(decrypt, paths)
