import jwt, datetime, os
from dotenv import load_dotenv
from flask import Flask, request
from flask_mongoengine import MongoEngine
from models import User

load_dotenv()

app = Flask(__name__)
mongodb = MongoEngine(app)

JWT_SECRET = os.environ.get("JWT_SECRET_KEY")

app.config["MONGODB_SETTINGS"] = os.environ.get('MONGO_URI')

def createJWT(username: str, secret: str, roles: dict, admin: bool):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) 
            + datetime.timedelta(days=1),
            "iat": datetime.datetime.now(tz=datetime.timezone.utc),
            "roles": roles,
            "admin": admin,
        },
        secret,
        algorithm="HS256"
    )

@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "missing credentials", 401
    
    # check db for username and password
    user = User.objects(email=auth.username).first_or_404()
    if not user:
        return "bad credentials", 401
    if not user.check_password(auth.password):
        return "bad credentials", 401
    return createJWT(auth.username, JWT_SECRET, user.roles, user.admin)

@app.route("/api/v1/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return "missing credentials", 400
    if User.objects(email=data["email"]).first():
        return "user exists", 409
    user = User(email=data["email"])
    user.set_password(data["password"])
    user.save()
    return "", 201

@app.route("/api/v1/auth/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]
    
    if not encoded_jwt:
        return "missing credentials", 401
    
    encoded_jwt = encoded_jwt.split(" ")[1]
    
    try:
        decoded = jwt.decode(
            encoded_jwt,
            JWT_SECRET,
            algorithms=["HS256"]
        )
    except:
        return "not authorized", 403
    
    return decoded, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8002)
