# A many-to-many relationship in database design involves multiple records in one table being associated with multiple records in another table
# typically implemented through a junction table linking the primary keys of both entities.

from db import db

class ItemTagModel(db.Model): # ItemTagModel is a model that represents a junction between tags and items

    __tablename__ = 'item_tag_junction'

    id = db.Column(db.Integer, primary_key=True)

    # create link between item and tag
    item_id = db.Column(db.Integer, db.ForeignKey("items.id")) # these must be unique and not null
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"))

    # So basically SQLAlchemy takes care of the junction table, so you dont need to query anything, when we add a tag to the an item it updates the table