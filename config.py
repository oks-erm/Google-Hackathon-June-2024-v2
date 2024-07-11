from flask import Flask
from flask_cors import CORS
from flask_caching import Cache
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI
import os
import redis


load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


# Redis configuration for session management
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'session:'
try:
    app.config['SESSION_REDIS'] = redis.StrictRedis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD
    )
except redis.exceptions.ConnectionError:
    print("Error: Unable to connect to Redis.")


# Redis configuration for caching
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_HOST'] = REDIS_HOST
app.config['CACHE_REDIS_PORT'] = REDIS_PORT
app.config['CACHE_REDIS_PASSWORD'] = REDIS_PASSWORD
app.config['CACHE_REDIS_URL'] = os.getenv('REDIS_URL')


supabase: Client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
cache = Cache(app)
openai = OpenAI()
