from email import message
from xml.dom import UserDataHandler
from flask.views import MethodView
from flask_smorest import Blueprint, abort # this allows us to send abort to requests in case of an error with documentation
from passlib.hash import pbkdf2_sha256 # hashing algorithm to hash password
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from flask_jwt_extended import create_access_token, get_jwt, jwt_required, create_refresh_token, get_jwt_identity
# the access token is going to be given to the user after a successfull login
# the access token is needed in every request so the user can access different resources that a JWT is needed

from db import db
from models import UserModel, BlocklistModel, blocklist # to access db for users we need to import the usermodel db
from schemas import UserSchema, UserRegisterSchema # to serialize and deserialize the user incoming data

import tasks
from flask import current_app

blp = Blueprint("Users", __name__, description="Operations on users")


@blp.route('/register')
class RegisterUser(MethodView):

    @blp.arguments(UserRegisterSchema) # we get username and password and email
    def post(self, register_user_data): #  1. get the username and password as json from the user

        # we could check if the user is already registered like so: # from sqlalchemy import or_
        # if UserModel.query.filter(or_(UserModel.username == register_user_data['username'],
        # UserModel.email == register_user_data['email'])).first():
            # abort(409, message="User already registered.")
        # But this is not needed because we set the username as unique, so if we try to insert it to the db we will get an IntegrityError
        # So if we get an Intergrity error we know that the user with that username already exists


        # 2. create a user and hash the password
        password = register_user_data['password']
        email = register_user_data['email']
        username = register_user_data['username']

        user = UserModel(email=email, username=username, password=pbkdf2_sha256.hash(password))

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            abort(409, message='User already exists or email already used.') # 3. if the user already exists we will get an integrity error
        except SQLAlchemyError:
             abort(500, message="An error occurred while creating the user")

        # After the user has create successfully, send email with documentation:
             
        # usually we would not want to use the app to send emails, so we need to set a redis queue.
        # at this queue, the app add the registered users and the redis queue pops and executed the email sending.
        # the background worker will handle the email sending and redis will hold the queue
        # we want to do it so we dont overload on the api.
        response = current_app.queue.enqueue(tasks.send_user_registration_email, user.email, user.username)
        # here we send the worker to run the function

        print('Send email with response of: ', response)

        return {"message": "User created successfully"}, 201 # 4. if successful return message



# NOTE - TESTING ONLY
@blp.route('/user/<int:user_id>')
class TestingUserInfo(MethodView):

    @blp.response(200, UserSchema) # return a user and id
    def get(self, user_id):

        user = UserModel.query.get_or_404(user_id)
        return user
    
    def delete(self, user_id):

        user = UserModel.query.get_or_404(user_id)

        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted"}, 200

@blp.route('/login')
class Login(MethodView):

    @blp.arguments(UserSchema) # parse username and password
    def post(self, user_data):

        user = UserModel.query.filter(UserModel.username == user_data['username']).first() # query by the username that the user gave us
        if user: # if the user exists, and the passwords match, get a jwt token
            if pbkdf2_sha256.verify(user_data['password'], user.password):
                access_token = create_access_token(identity=user.id, fresh=True) # identity = to know which user logged, fresh = the JWT is fresh after login
                refresh_token = create_refresh_token(identity=user.id)
                return {"JWT": access_token, "RefreshToken": refresh_token}, 200
            else: # if the password do not match, abort
                abort(401, message="Passwords do not match.")
        else: # if the user doesnt exist, abort.
            abort(401, message="User doesn't Exist, please register.")


@blp.route('/logout')
class Logout(MethodView):
    
    # We done need a schema, because we dont recieve anything from the user in the body. The JWT is in the header.
    @jwt_required()
    def post(self): # take the JTI (unique JWT identifier) and add it to the blocklist
         
        jti = get_jwt().get('jti') # save the JTI in the DB
        record = BlocklistModel(jti=jti)

        try:
            db.session.add(record)
            db.session.commit()
        except IntegrityError:
            abort(409, message='JWT already revoked.')
        except SQLAlchemyError:
             abort(500, message="An error occurred while revoking JWT")

        return {"message": "logged out successfully"}, 201

@blp.route('/refresh')
class Refresh(MethodView):

    @jwt_required(refresh=True) # if the user wants to refresh his token, he needs a refresh token 
    def post(self):

        access_token = create_access_token(identity=get_jwt_identity(), fresh=False) # set identity as same, but non-fresh

        # the refresh token can be used once.
        jti = get_jwt().get('jti')
        record = BlocklistModel(jti=jti)
        try:
            db.session.add(record)
            db.session.commit()
        except IntegrityError:
            abort(409, message='Refresh token already revoked.')
        except SQLAlchemyError:
             abort(500, message="An error occurred while revoking JWT")

        return {"access_token": access_token}