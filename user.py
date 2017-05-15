import hashlib
import os
import pickle


class User:
    users_path = 'users.pkl'

    def __init__(self, password):
        self.password = hashlib.sha256(password.encode()).hexdigest()
        self.salt = self.get_salt()

    def get_users(self):
        try:
            with open(self.users_path, 'rb') as i:
                return pickle.load(i)

        except FileNotFoundError:
            return {}

    def get_salt(self):
        users = self.get_users()
        if self.password not in users:
            self.create()
            return self.get_salt()

        return users[self.password]

    def create(self):
        users = self.get_users()
        users[self.password] = os.urandom(16)

        with open(self.users_path, 'wb') as o:
            return pickle.dump(users, o)
