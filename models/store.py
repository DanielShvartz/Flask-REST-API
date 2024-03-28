from db import db

# Database models using SQLAlchemy in Flask represent the structure and behavior of data entities within the application
# enabling seamless interaction with the database through object-oriented programming paradigms.

class StoreModel(db.Model):

    __tablename__ = "stores"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    
    items = db.relationship("ItemModel", back_populates="store", lazy="dynamic", cascade="all, delete")
    tags = db.relationship("TagModel", back_populates="store", lazy="dynamic")
    # lazy = "dynamic" means that it will not load the items until we ask it to. if it was not dynamic it would load all the tags
    # "cascade, delete" means that if we delete the parent, all of the children will be also deleted