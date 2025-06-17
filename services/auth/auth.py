import os
from datetime import datetime, timezone, timedelta
from flask import Blueprint, redirect, url_for, request, jsonify
from authlib.integrations.flask_client import OAuth
from flask_jwt_extended import create_access_token
from models import User, OAuthAccount, pwd_ctx

oauth = OAuth()
auth_v1_bp = Blueprint("auth_v1", __name__)

@auth_v1_bp.record
def init_oauth(state):
    oauth.init_app(state.app)
    # configure providers
    oauth.register(
        name="google",
        client_id=state.app.config["OAUTH_GOOGLE_CLIENT_ID"],
        client_secret=state.app.config["OAUTH_GOOGLE_CLIENT_SECRET"],
        access_token_url="https://oauth2.googleapis.com/token",
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        client_kwargs={"scope":"openid email profile"},
    )
    oauth.register(
        name="microsoft",
        client_id=state.app.config["OAUTH_MICROSOFT_CLIENT_ID"],
        client_secret=state.app.config["OAUTH_MICROSOFT_CLIENT_SECRET"],
        access_token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
        authorize_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        client_kwargs={"scope":"openid email profile"},
    )
    oauth.register(
        name="azuread",
        client_id=state.app.config["OAUTH_AZUREAD_CLIENT_ID"],
        client_secret=state.app.config["OAUTH_AZUREAD_CLIENT_SECRET"],
        access_token_url=f"https://login.microsoftonline.com/{state.app.config['OAUTH_AZUREAD_TENANT']}/oauth2/v2.0/token",
        authorize_url=f"https://login.microsoftonline.com/{state.app.config['OAUTH_AZUREAD_TENANT']}/oauth2/v2.0/authorize",
        client_kwargs={"scope":"openid email profile"},
    )

@auth_v1_bp.route("/<provider>/login")
def oauth_login(provider):
    redirect_uri = url_for("auth_v1.oauth_callback", provider=provider, _external=True)
    return oauth.create_client(provider).authorize_redirect(redirect_uri)

@auth_v1_bp.route("/<provider>/callback")
def oauth_callback(provider):
    client = oauth.create_client(provider)
    token = client.authorize_access_token()
    userinfo = client.parse_id_token(token)
    sub = userinfo["sub"]  # or "oid"/"email" depending on provider

    # find or create OAuthAccount
    acct = OAuthAccount.objects(provider=provider, provider_user_id=sub).first()
    if not acct:
        # first time: create User + OAuthAccount
        user = User(email=userinfo["email"], active=True)
        user.set_password(os.urandom(24).hex())  # random pw
        user.save()
        acct = OAuthAccount(
            user=user,
            provider=provider,
            provider_user_id=sub
        )

    # update tokens & expiry
    acct.access_token  = token["access_token"]
    acct.refresh_token = token.get("refresh_token")
    expires_ts = token.get("expires_in")
    acct.expires_at    = datetime.now(timezone.utc) + timedelta(seconds=expires_ts)
    acct.save()

    # issue our JWT
    jwt_token = create_access_token(identity=str(acct.user.id))
    return jsonify(access_token=jwt_token)

@auth_v1_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    user = User(email=data["email"], active=True)
    user.set_password(data["password"])
    user.save()
    return jsonify(message="registered"), 201

@auth_v1_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.objects(email=data["email"]).first_or_404()
    if not user.check_password(data["password"]):
        return jsonify(msg="Bad credentials"), 401
    token = create_access_token(identity=str(user.id))
    return jsonify(access_token=token)
