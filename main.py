#!/home/lukas/Tester/Python/locker/env/bin/python3

from locker import Encryptor, Decryptor
from argparse import ArgumentParser
from getpass import getpass


def ask_password(register=True):
    '''
    Ask the user to give a password. If 'register' is true, then it will verify the
    given password and recursively ask the user again if it doesn't match.
    Otherwise, if 'register' is false, then it will just return the given 
    password.
    '''
    password = getpass()

    if register:
        verify_password = getpass('Confirm Password: ')
        if password != verify_password:
            print()
            print("The password doesn't match. Please try again.")
            return ask_password()
    print('Accepted!')
    return password


def main():
    parser = ArgumentParser()
    parser.add_argument('files', nargs='+')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e', action='store_true')
    group.add_argument('-d', action='store_true')
    args = parser.parse_args()

    if args.e:
        encryptor = Encryptor(args.files, ask_password(register=True))
        encryptor.start()
    else:
        decryptor = Decryptor(args.files, ask_password(register=False))
        decryptor.start()


if __name__ == '__main__':
    main()
