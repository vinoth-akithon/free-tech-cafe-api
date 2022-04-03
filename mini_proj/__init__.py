from distutils.log import debug
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
# from flask_restful import Api
from flask_cors import CORS

print("pass1")
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data_base.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "DWSFGWSFWBEFWHFUIU"
db = SQLAlchemy(app)
cors = CORS(app)

from .views import *
from .urls import *


app.config['JWT_SECRET_KEY'] = "whgfuherfguywenscse"
jwt = JWTManager(app)

# app.config['JWT_BLACKLIST_ENABLED'] = True
# app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

if __name__ == "__main__":
    app.run(debug=True)