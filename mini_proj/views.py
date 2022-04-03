from flask import jsonify, request,render_template,make_response
from mini_proj import app
from .models import *
from flask_jwt_extended import create_access_token,create_refresh_token,jwt_required,get_jwt_identity


def register_view():
   
    email = (request.form["email"]).lower()
    if not User.check_user(email):
        new_user = User(name=(request.form["name"]).capitalize(),
                        email=email,
                        password=genearte_hash(request.form["password"]))
        new_user.save_to_db()
        return make_response(jsonify({"message":"Thanks for registering with us!",
                            "access_token": create_access_token(email),
                            "refresh_token":create_refresh_token(email)}),200)
    else:
        return make_response({"message":"You are already registerd with us,Please login!"},400)


def login_view():
    email = (request.form["email"]).lower()
    user = db.session.query(User).filter_by(email = email).first()
    if not user:
        return make_response({"message":"You are not registered with us.Please register!"},400)

    if not verify_hash(request.form["password"],user.password):
        return make_response({"message": "Password is incorrect!"},400)
    
    return make_response({"message":"login successful!",
                        "access_token": create_access_token(email),
                        "refresh_token":create_refresh_token(email)},200)


@jwt_required()
def home():
    identity = get_jwt_identity()
    print(identity)
    user = db.session.query(User).filter_by(email = identity).first()
    if not user:
        return make_response({"message":"Authorization failed"},400)
    print("passed")
    return make_response({"message": user.name},200)


@jwt_required()
def logout_view():
    identity = get_jwt_identity()
    return make_response({"message":"loged out successfully"},200)