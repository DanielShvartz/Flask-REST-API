from db import db


class UserModel(db.Model):

    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True) # each time we add a user to the table it will assign it an id
    username = db.Column(db.String(80), unique=True, nullable=False) # the username needs to be unique
    password = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False, unique=True)