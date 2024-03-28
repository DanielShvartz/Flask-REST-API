from pprint import pp
from flask.views import MethodView
from flask_smorest import Blueprint, abort # this allows us to send abort to requests in case of an error with documentation
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import TagModel, StoreModel, ItemModel # to access db for tags, and tags within stores, and items
from schemas import TagSchema, TagAndItemSchema # to serialize and deserialize

blp = Blueprint("tags", __name__, description="Operations on tags")


@blp.route('/tag/<int:tag_id>')
class Tag(MethodView):

    @blp.response(200, TagSchema)
    def get(self, tag_id):
        
        # we need to query by the tag id because we can get the information regardless
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    
    @blp.response(202, description='Deletes a tag if no item is tagged with it', example={"message": "Tag deleted."}) # main response
    @blp.alt_response(404, description='Tag not found', example={"message": "Tag not found"})
    @blp.alt_response(400, description="Returned if the tag is assigned to one or more items. In this case, the tag is not deleted. To delete the tag, remove items associated")
    def delete(self, tag_id): # remove the tag from the store
        
        tag = TagModel.query.get_or_404(tag_id)
        if tag.items: # if the tag has items
            abort(400, message="Tag is associated with items, could not delete tag.")
        else: # if the tag doesnt have items 
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted successfully"} # 202


@blp.route('/store/<int:store_id>/tag') # if we can a request to /store/store_id/tag
class TagsInStore(MethodView):

    # get request with only store id passed
    # return many tags that are part of the store
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        #return TagModel.query.all(store_id)
        store =  StoreModel.query.get_or_404(store_id) # get all the stores with the store id
        return store.tags.all() # we can access tags, because we declared a relationship to TagModel, and we fetch all the tags

    # receive request to create a new tag, return a tag
    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id): # because we receive data, first parse the tag_data and then the store_id
        
        # we can also check for if a store (with the store_id) has already the tag (with the tag_name), but since the name of the tag is unique, we dont need to
        # if TagModel.query.filter(TagModel.store_id == store_id, TagModel.name == tag_data["name"]).first(): abort()
        # this querys the TagModel table, and filters by the store_id and the tag_name, and takes the first result, if there is a result it aborts.

        tag = TagModel(**tag_data, store_id=store_id) # create a TagModel object, with a store_id as given

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e)) # if we have an item in the same store or the store id doesnt exist - error
        return tag

@blp.route('/item/<int:item_id>/tag/<int:tag_id>')
class LinkTagsToItems(MethodView):

    @blp.response(201, TagSchema)
    @blp.alt_response(400, description='Cannot link item from one store to tag from another store.')
    def post(self, item_id, tag_id): # when we link an item_id to tag_id, we need to add a record to the junction table
        
        # we first want to find the item and the tag, and then link them
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        # when we link a tag to an item, we want to make sure that they are from the same store.
        # because we cant link a tag from store A to an item in store B.
        if tag.store.id != item.store.id:
            abort(400, message='Cannot link item from one store to tag from another store. Make sure both tag and item are from the same store.')

        # add the tag to the tags list of the item, so we link the tag to the item
            
        item.tags.append(tag)
        try:
            db.session.add(item) # insert the tag into the list of tags of an item in the db
            db.session.commit() # this commit update the records in the junction table to reflect the new association between item and tag
        # So basically SQLAlchemy takes care of the junction table, so you dont need to query anything, when we add a tag to the an item it updates the table
        except SQLAlchemyError:
            abort(500, message="Some error occured while inserting the tag")
        
        return tag

    @blp.response(200, TagAndItemSchema) # we return the tag and the item and a message
    @blp.alt_response(400, description='Cannot detach item from one store to tag from another store.')
    def delete(self, item_id, tag_id): # when we detach an item_id to tag_id, we need to delete a record from the junction
        
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        if tag.store.id != item.store.id:
            abort(400, message='Cannot detach item from one store to tag from another store. Make sure both tag and item are from the same store.')

        item.tags.remove(tag)
        try:
            db.session.add(item) # update db
            db.session.commit() # sqlalchemy updates the junction table
        except SQLAlchemyError:
            abort(500, message="Some error occured while detaching the tag")
        
        return {"message": "Item removed from tag", "item": item, "tag": tag} # TagAndItemSchema will parse this
