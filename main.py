from locker import Encryptor, Decryptor
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

    if args.e:
        encryptor = Encryptor(args.file, password)
        encryptor.start()
    else:
        decryptor = Decryptor(args.file, password)
        decryptor.start()


if __name__ == '__main__':
    main()
