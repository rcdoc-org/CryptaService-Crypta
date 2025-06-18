import os, json
from flask import Flask, request
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access

server = Flask(__name__)
server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/docs"

mongo = PyMongo(server)

@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)

    if not err:
        return token
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


