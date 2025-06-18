import flask
try:
    # older Flask
    from flask.json import JSONEncoder
except ImportError:
    # Flask ≥2.3 moved JSONEncoder into the provider
    from flask.json.provider import DefaultJSONProvider as JSONEncoder

# inject it so `from flask.json import JSONEncoder` works again
flask.json.JSONEncoder = JSONEncoder

import os
from flask import Flask, request
from flask_cors import CORS
from flask_mongoengine import MongoEngine
from flask_security import Security, MongoEngineUserDatastore
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from auth import auth_v1_bp
from models import Role, User, Profile


load_dotenv()

db = MongoEngine()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        MONGODB_SETTINGS = { "host": os.getenv("MONGO_URI") },

        SECRET_KEY = os.getenv("SECURITY_KEY"),
        JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY'),
        SECURITY_REGISTERABLE = True,
        SECURITY_SEND_REGISTER_EMAIL = False,
        
        # Oauth Client Creds:
        OAUTH_GOOGLE_CLIENT_ID=os.getenv("GOOGLE_ID"),
        OAUTH_GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_SECRET"),
        OAUTH_MICROSOFT_CLIENT_ID=os.getenv("MS_ID"),
        OAUTH_MICROSOFT_CLIENT_SECRET=os.getenv("MS_SECRET"),
        OAUTH_AZUREAD_CLIENT_ID=os.getenv("AAD_NFP_ID"),
        OAUTH_AZUREAD_CLIENT_SECRET=os.getenv("AAD_NFP_SECRET"),
        OAUTH_AZUREAD_TENANT=os.getenv("AAD_NFP_TENANT"),
        
        # Plan to send emails later:
        # MAIL_SERVER=…,
        # MAIL_USERNAME=…,
        # MAIL_PASSWORD=…,
    )
    
    db.init_app(app)
    jwt.init_app(app)
    Security(app, MongoEngineUserDatastore(db, User, Role))
    app.register_blueprint(auth_v1_bp, url_prefix="/api/v1/auth")
    return app

app = create_app()

# allow cross-origin requests from the front-end dev server
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
CORS(
    app,
    origins=[frontend_origin],
    supports_credentials=True,
)

if __name__ == "__main__":
    app.run(debug=True)