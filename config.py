from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SESSION_PSWD'
app.config['SECRET_KEY'] = os.urandom(24)
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

formatted_private_key = os.getenv('GOOGLE_PRIVATE_KEY', '').replace("\\n", "\n")
if formatted_private_key is None:
    raise ValueError("GOOGLE_PRIVATE_KEY is not set")

creds_dict = {
    "type": os.getenv('GOOGLE_TYPE', ''),
    "project_id": os.getenv('GOOGLE_PROJECT_ID', ''),
    "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID', ''),
    "private_key": formatted_private_key,
    "client_email": os.getenv('GOOGLE_CLIENT_EMAIL', ''),
    "client_id": os.getenv('GOOGLE_CLIENT_ID', ''),
    "auth_uri": os.getenv('GOOGLE_AUTH_URI', ''),
    "token_uri": os.getenv('GOOGLE_TOKEN_URI', ''),
    "auth_provider_x509_cert_url": os.getenv('GOOGLE_AUTH_PROVIDER_X509_CERT_URL', ''),
    "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL', '')
}

# Create a db instance
db = SQLAlchemy(app)