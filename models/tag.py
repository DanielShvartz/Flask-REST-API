from db import db


# db.relationship explenation - when we do a relationship we set access to another table. in this case we have a store and we define a relationship to the 
# StoreModel, meaning that we can access that store. if we dont write back_populates only tag will be able to access store. if we write back_populates then
# store can also access tags, so its bidirectional.

# back_populates explenation - with this we can set a bidirectional navigation, if we dont write it, it will be only 1 way navigation.
# we need to specify the relationship in both classes!!!

class TagModel(db.Model):

    __tablename__ = "tags"
    
    id = db.Column(db.Integer, primary_key=True) # id of a tag
    name = db.Column(db.String(80), unique=True, nullable=False) # name of a tag needs to unique 

    # store_id that is related to, if the store_id was unique we had only 1 tag to 1 store
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), nullable=False) 
    store = db.relationship("StoreModel", back_populates="tags") # store itself as inforamtion so we can see info about the store with the tag
    
    # this tells sqlalchemy that it has to go through the tags and item_tag_junction in order to get the items
    # it will go on the id of the current tag and return us the items corresponding to that tag_i
    items = db.relationship("ItemModel", back_populates="tags", secondary="item_tag_junction")