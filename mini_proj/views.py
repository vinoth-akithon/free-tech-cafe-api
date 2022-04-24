from flask import jsonify, request,make_response,redirect
import os,json,requests
from dotenv import load_dotenv
from mini_proj import app,jwt
from .models import *
from flask_jwt_extended import create_access_token,create_refresh_token,jwt_required,get_jwt_identity,get_jwt
from oauthlib.oauth2 import WebApplicationClient
import logging
import pyotp


logging.basicConfig(level=logging.DEBUG)
load_dotenv()
# getting secret value from env
google_client_id = "891120027637-eenuem9abguslv240n5df1eqsgni3qk4.apps.googleusercontent.com"
google_client_secret = "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"
authorization_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
token_endpoint = "https://oauth2.googleapis.com/token"
userinfo_endpoint = "https://openidconnect.googleapis.com/v1/userinfo"
redirect_uri = "https://veeramvinoth.pythonanywhere.com/callback"
frontend_url = "https://vinoth-kumar-m-1026.github.io/free_tech_cafe_ui"


def index():
    logging.info(google_client_id)
    return "<h1 style='color:green;margin:auto;width:80%;text-align:center;font-size:10vw'>Hello World</h1>"

def register_view():
    if request.method == "GET":
        client = WebApplicationClient(google_client_id)
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=redirect_uri,
            scope=["openid", "email", "profile"],
        )
        return ({"url":request_uri})

    else:
        email = (request.form["email"]).lower()
        if not User.check_user(email):
            google_secret = str(pyotp.random_base32())
            google_uri = pyotp.totp.TOTP(google_secret).provisioning_uri(issuer_name="BONAI")
            # qrcode_uri = f"https://www.google.com/chart?chs=200x200&chld=M|0&cht=qr&chl={google_uri}"
            qrcode_uri = google_uri

            User(name=(request.form["name"]).capitalize(),
                        email=email,
                        google_secret=google_secret,
                        qrcode_uri=qrcode_uri,
                        password=genearte_hash(request.form["password"])).save_to_db()
            return make_response(jsonify({"message":"Thanks for registering with us!",
                                "google_secret": google_secret,
                                "qrcode_uri":qrcode_uri
                                }),200)
        else:
            return make_response({"message":"You are already registerd with us,Please login!"},400)


def login_view():
    if request.method == "GET":
        client = WebApplicationClient(google_client_id)
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=redirect_uri,
            scope=["openid", "email", "profile"],
        )
        return ({"url":request_uri})

    else:
        print("pass")
        email = (request.form["email"]).lower()
        user = db.session.query(User).filter_by(email = email).first()
        if not user:
            return make_response({"message":"You are not registered with us.Please register!"},400)

        if not verify_hash(request.form["password"],user.password):
            return make_response({"message": "Password is incorrect!"},400)

        otp = request.form["otp"]
        secret = user.google_secret
        if not pyotp.TOTP(secret).verify(otp):
            return make_response({"message": "authendication failed due to invalid otp!"},401)
        
        return make_response({"message":"login successful!",
                            "access_token": create_access_token(email)},200)

@app.route("/callback",methods=["GET"])
def callback():
    client = WebApplicationClient(google_client_id)
    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        redirect_url=redirect_uri,
        code=request.args.get("code")
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(google_client_id, google_client_secret),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    uri, headers, body = client.add_token(userinfo_endpoint)
    
    # send request to user info api for getting basic infos
    userinfo_response = (requests.get(uri, headers=headers, data=body)).json()
    email = userinfo_response["email"]
    user = User.check_user(email)
    if not user:
        User(name=userinfo_response["given_name"],email=email).save_to_db()
    access_token = create_access_token(email)
    
    return redirect(f"{frontend_url}/dummy.html?access_token={access_token}")
                            

@jwt_required()
def home():
    identity = get_jwt_identity()
    user = User.check_user(identity)
    if not user:
        return make_response({"message":"Authorization failed"},400)
        
    return make_response({"message": user.name},200)


@jwt_required()
def logout_view():
    jti = get_jwt()["jti"]
    TokenBlocklist(jti=jti).save_to_db()
    return make_response({"message":"loged out successfully"},200)


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist).filter_by(jti=jti).first()
    return token is not None

# db.session.close_all()

# @app.route("/login")
# def login():
#     user_name = "vinoth"
#     password = "12345"
#     if request.form["user_name"] == "vinoth" and request.form["password"] == "12345":
#         secret_key = pyotp.random_base32()
#         return make_response({"secret_key": secret_key},200)
#     else:
#         return make_response({"message":"authendication failed"},401)


# @app.route("/verify")
# def verify():
#     otp = request.form["otp"]
#     secret = request.form["secret"]
#     if pyotp.TOTP(secret).verify(otp):
#         return make_response({"message": "authendication secceed!"},200)
#     else:
#         return make_response({"message": "otp verification failed."},401)
