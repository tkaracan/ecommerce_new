import os
from dotenv import load_dotenv
from pathlib import Path


env_path = Path('.') / 'env.env'
load_dotenv(dotenv_path=env_path)
print('hello')

class GlobalConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    CORS_IP = os.getenv('CORS_IP')
    CORS_PORT = os.getenv('CORS_PORT')