from os import environ

DATABASE_URL = environ.get("DATABASE_URL")
MAIN_URL = environ.get("MAIN_URL")

SECRET_KEY = environ.get("SECRET_KEY")
