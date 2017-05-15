#!env/bin/python3

from locker import Encryptor, Decryptor
from user import User
from argparse import ArgumentParser
from getpass import getpass


def main():
    parser = ArgumentParser()
    parser.add_argument('file', type=str)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e', action='store_true')
    group.add_argument('-d', action='store_true')
    args = parser.parse_args()

    password = getpass()

    user = User(password)

    if args.e:
        encryptor = Encryptor(args.file, user)
        encryptor.encrypt()
    else:
        decryptor = Decryptor(args.file, user)
        decryptor.decrypt()


if __name__ == '__main__':
    main()
