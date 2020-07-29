import bcrypt

from app import mongo


class User:
    def __init__(self, email):
        self.email = email

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.email

    @staticmethod
    def check_password(password_hash, password):
        return bcrypt.hashpw(password.encode('utf-8'), password_hash) == password_hash

    @staticmethod
    def find_one(email):
        return mongo.db.Users.find_one({'email': email})

    @staticmethod
    def insert(email, password):
        return mongo.db.Users.insert({'email': email, 'password': password})