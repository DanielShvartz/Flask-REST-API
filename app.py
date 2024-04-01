from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

# import the blp vars from the items and stores files to register them
from models.blocklist import BlocklistModel
from resources.stores import blp as StoreBluePrint
from resources.items import blp as ItemBluePrint
from resources.tags import blp as TagBluePrint
from resources.users import blp as UserBluePrint

from db import db
import models # inside-> StoreModel and ItemModel.  The models are needed to be declared before the init of sqlalchemy so it will know which models are available

import os
from dotenv import load_dotenv
import redis
from rq import Queue
""" 
NOTE:
There are two parts of the flask route: the endpoint decorator and the function that should run
The decorator registers the endpoint with Flask. So flask knows that when we will receive a get request
on /url/store (for an example) it will run the function. The function does something and returns JSON

If a server returns as an error 500, it means that something is fucked up.
This is caused where the function did not return a valid response.
And returned either None or without a return.

To run the app: in the terminal: flask run 
Then we will have an address to connect to and send reqests there
The data that we send to that address will be fowarded to the app """

# This function configures and creates a flask app. instead of running app.py we call that function.
def create_app(db_url=None):

    app = Flask(__name__) # This creates a flask instance/app, allows us to also run the app
    load_dotenv() # load environment variables

    connection = redis.from_url(os.getenv("REDIS_URL")) # create a connection to redis
    app.queue = Queue('emails', connection=connection)

    # Register blueprints with the api
    app.config["PROPAGATE_EXCEPTIONS"] = True # if there is an exception - propagate it to the main app so we can see it
    # Flask Smorest configuration
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "V1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/" # where the root is, we start with / 
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui" # use swagger to document the api
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/" # load files from the url

    # use SQLAlchemy with a connection string to connect to the database. In this case, flask app is the client connecting to the db
    # store the data in data.db. if we have a db_url, use it, if not -> try to access the environment variable called DATABASE_URL
    # if the user doesnt specify a database url, it will take the sqlite url
    app.config["SQLALCHEMY_DATABASE_URI"] =  db_url or os.getenv("DATABASE_URL", "sqlite:///data.db") 
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app) # init the database with the flask app

    migrate = Migrate(app, db)

    # ACCESS SWAGGER UI DOCUMENTATION AT - http://localhost:5000/swagger-ui

    # each time we will load the app it will create a new secret key, and its no convienient, so we set it here, and later store it.
    app.config["JWT_SECRET_KEY"] = '335460259817775594435160938215214609462' # str(secrets.SystemRandom.getrandbits(k=128))  # create a secret key. 
    api = Api(app) # connect the flask smorest extention to the flask app

    jwt = JWTManager(app) # create an instance of the JWTManager

    # JWT Claims adding: These function will be run each time we create a JWT for a user.

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (jsonify({'description': 'The token is not fresh', "error": "fresh_token_required"}), 401,)

    @jwt.token_in_blocklist_loader # each time we receive a JWT this function will be run
    def check_if_JWT_in_blocklist(jwt_header, jwt_payload):
        return models.BlocklistModel.query.filter(BlocklistModel.jti == jwt_payload['jti']).first()
        # query for the jti. if he exists in the blocklist db, this returns true, and means that the user loggout out and his JWT is revoked
        # if the query returns none, then the user is still logged in and didn't logged out.
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload): # if token is revoked
        return (jsonify({"message":"This token has been revoked", "error": "token_revoked"}), 401,)

    @jwt.additional_claims_loader # We can add more info to the JWT, like if the user is an administrator by its id/name
    def add_claims_to_JWT(identity):
        if identity == 1: 
            return {"admin": True} 
        return {"admin": False}
    # this is not ideal, its better to add a column in the user db stating that if he is admin or not
    # and then when reciving a request we would take the identity from the JWT, and compare it in the db to know if its an admin.

    # JWT Error Handling: - need to return a json with a tuple, message and error code
    # Notice that the we cannot return dict, we must import jsonify
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload): # here the JWT is valid but expired, so we give it a payload and header
        return (jsonify({"message":"The token has expired", "error": "token_expired"}), 401,)

    @jwt.invalid_token_loader
    def invalid_token_callback(error): # here the JWT is invalid at all so we cannot access the header/payload
        return (jsonify({"message": "Signature verification failed.", "error": "invalid_token"}), 401,)

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (jsonify({"description": "Request doesn't contain a JWT.", "error": "authorization_required"}), 401,)

    
    # SINCE WE ARE USING MIGRATE, WE DONT NEED SQLALCHEMY CREATING OUR TABLES. SO WE CAN REMOVE THE DB.CREATE_ALL()
    #   with app.app_context():
    #       db.create_all() # before we proccess any requests, create the tables. if the tables already exist, it wont create them

    # add blueprints, the blueprints are the blp vars that we set on the stores and items files
    api.register_blueprint(ItemBluePrint)
    api.register_blueprint(StoreBluePrint)
    api.register_blueprint(TagBluePrint)
    api.register_blueprint(UserBluePrint)

    return app


# docker run --name store_api -p 5000:5000 -it -v ${PWD}:/app store_api