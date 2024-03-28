from db import db # to get that sqlalchemy instance in the item.py

# any class that we create can map himself to a column and sqlalchemy will be able to turn the rows to object
# mapping between a row into a class. i.e convert row -> class instance
class ItemModel(db.Model):
    
    __tablename__ = "items" # create and use the table named items for this class and all of his instances
    
    # declare columns
    # unique -> cannot have the same name/id, must be one.
    # primary_key -> cannot be null and must be unique. the db will give a number be order

    id = db.Column(db.Integer, primary_key=True) # id is going to be the the unique identifier of the item, and will be assigned by the db
    
    # user needs to pass:
    name = db.Column(db.String(80), unique=False, nullable = False)
    price = db.Column(db.Float(precision=2), unique=False, nullable = False)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), unique=False, nullable = False) # link to the store table. foreign key is used to map the store_id to the id of the store

    # we can also save a StoreModel object with a given store_id and then we can access the store
    store = db.relationship("StoreModel", back_populates="items") # this way if we have a store_id we can have a store object of that same id.

    tags = db.relationship("TagModel", back_populates="items", secondary="item_tag_junction") # many to many relationship declarations

    description = db.Column(db.String())
    

# A one-to-many relationship - one entity (or record) in a table is associated with multiple entities (or records) in another table.
# For an example we can have one store, and 5 items that have the store_id of that same store, so we can say they relate to the same store.


print('check')