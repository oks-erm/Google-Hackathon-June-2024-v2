from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from supabase import create_client, Client
from openai import OpenAI
import os
import redis


load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.urandom(24)

# Redis configuration
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'session:'
app.config['SESSION_REDIS'] = redis.StrictRedis.from_url(os.getenv('REDIS_URL'))

# change this
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

supabase: Client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
openai = OpenAI()
