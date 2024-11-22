from os import environ

DATABASE_URL = environ.get("DATABASE_URL")
MAIN_URL = environ.get("MAIN_URL")

SECRET_KEY = environ.get("SECRET_KEY")

KAFKA_BROKER_URL = environ.get("KAFKA_BROKER_URL")
KAFKA_TOPIC = environ.get("KAFKA_TOPIC")
print(KAFKA_BROKER_URL, KAFKA_TOPIC)
