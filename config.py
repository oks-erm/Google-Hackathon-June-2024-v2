from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from supabase import create_client, Client
from openai import OpenAI
import os
import redis

import os
import base64
import binascii


load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


# Redis configuration
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'session:'
app.config['SESSION_REDIS'] = redis.StrictRedis(
                        host=os.getenv('REDIS_HOST'),
                        port=os.getenv('REDIS_PORT'),
                        password=os.getenv('REDIS_PASSWORD')
						)


# change this
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

supabase: Client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
openai = OpenAI()
