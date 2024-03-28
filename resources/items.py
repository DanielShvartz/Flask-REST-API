from flask.views import MethodView
from flask_smorest import Blueprint, abort # this allows us to send abort to requests in case of an error with documentation
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema

from flask_jwt_extended import jwt_required, get_jwt


# Blueprints in Flask are needed for organizing routes, views, and resources into modular components
# facilitating the structuring of large applications and promoting code reusability.

# DEFINITION OF AN ITEM: ITEM_ID, STORE_ID, NAME, PRICE

# A blueprint in flask_smorest is used to divide the API into multiple segments.
blp = Blueprint("items", __name__, description="Operations on items") # to link between 2 blueprints, named as items


@blp.route("/item")
class ItemList(MethodView):

    @blp.response(200, ItemSchema(many=True)) # because we return alot of values we need to allows the schema to accept many schemas
    def get(self):
        return ItemModel.query.all()
    
    @jwt_required() # the user needs a JWT to create an item
    # this will use schema to check that store_id, price, name are in the request
    # and it will also check for types, store_id is str, price is float, name is str
    @blp.arguments(ItemSchema)
    # Post request -> Add item to the items table
    # The request should look like this: {store_id: 123, item_price: 456, item_name: 789}
    @blp.response(201, ItemSchema)
    def post(self, item_data): # item data will be the validated json of the body of the request
        item = ItemModel(**item_data) # parse the item data from the user to ItemModel object. (doesnt save to db yet)
        # try to access the db and add the item. any issues that will be raised will also be caught
        try:
            # we will get the ID of the item and check uniquness of columns only when we save it to the db.
            db.session.add(item) # add the item but not saved to the db
            db.session.commit() # save to db
        except SQLAlchemyError:
            abort(500, message="An error occurred while creating the item") # if we have an item in the same store or the store id doesnt exist - error
        return item
    
        # BUG: we can create an item that have a store_id but the store doesnt exist, it will be fixed with migration to postgresql -> need to throw an error
    
    
@blp.route("/item/<int:item_id>")
class Item(MethodView):

    # main success response - return 200, with name, price, store_id, and always return the item_id
    @blp.response(200, ItemSchema)
    def get(self, item_id): # get item using its id
        item = ItemModel.query.get_or_404(item_id)  # query the db.model with the item id, and if he doesnt exist return 404
        # because the ID is unique we will get only 1 item each time
        return item

    @jwt_required(fresh=True) # if the fresh = True then the access token must be fresh to delete an item
    def delete(self, item_id):

        # WE CAN CHECK CLAIM EITHER WHEN WE CREATE A JWT, OR WHEN WE RECIEVE A JWT.

        JWT = get_jwt() # THIS IS HOW WE ACCESS THE JWT
        if not JWT.get('admin'): # if the user is an admin, he can delete the item.
            abort(401, message="No admin permission to delete an item")

        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": f"Item deleted successfully"}

    @jwt_required()
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema) # response in case of successful update
    def put(self, item_data, item_id): # here we want to get to the same state at each request, if it either worked or not (200)
        item = ItemModel.query.get(item_id) # query for the item by its ID
        if item: # if the item exists - update
            item.name = item_data["name"]
            item.price = item_data["price"]
        else: # if the item doesn't exist - create new and assign the id given by the usedr
            item = ItemModel(id=item_id, **item_data) # the user needs to pass also the store id
        
        db.session.add(item)
        db.session.commit()
        return item