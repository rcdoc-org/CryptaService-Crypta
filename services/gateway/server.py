import os
import json
from flask import Flask, request
from flask_pymongo import PyMongo
from flask_cors import CORS
from auth import validate
from auth_svc import access

server = Flask(__name__)
server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/docs"

# Enable Cross-Origin Resource Sharing so the frontend can call the gateway from
# different origins (e.g. when the UI is served from a separate container or
# host).  "supports_credentials" allows cookies/authorization headers to be
# passed through when present.
CORS(server, supports_credentials=True)

mongo = PyMongo(server)

@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)

    if not err:
        return token
    else:
        return err

@server.route("/register", methods=["POST"])
def register():
    resp, err = access.register(request)
    if not err:
        return resp
    else:
        return err
    
@server.route("/validate", methods=["POST"])
def validate():
    access, err = validate.token(request)
    
    if not err:
        return access
    else:
        return err

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=3000)


