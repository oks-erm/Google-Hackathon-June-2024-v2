from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from supabase import create_client, Client
from openai import OpenAI
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'SESSION_PSWD'
app.config['SECRET_KEY'] = os.urandom(24)

os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
supabase: Client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
openai = OpenAI()