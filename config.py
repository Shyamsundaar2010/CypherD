import os

'''DB_USER = "postgres"
DB_PASS = "1007"
DB_HOST = "localhost"
DB_NAME = "wallet_db"'''

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1007@localhost/wallet_db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.urandom(24)
