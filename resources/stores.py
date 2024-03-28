from sqlite3 import IntegrityError
from flask.views import MethodView
from flask_smorest import Blueprint, abort # this allows us to send abort to requests in case of an error with documentation
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import StoreModel
from schemas import StoreSchema

# A blueprint in flask_smorest is used to divide the API into multiple segments.
blp = Blueprint("stores", __name__, description="Operations on stores") # to link between 2 blueprints, named as stores


# here we create a different class because the route is different
@blp.route("/store")
class StoreList(MethodView):
    
    # Here we are creating a function that will return a json that its key is the store id and the value its the store name and store id
    # This will be decorated using the app.get("/store") method which tells that the app can receive a get request
    # request to X.X.X.X/store and will return all the stores
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    # Post request - Example would be /store {"name": "store_name"}
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):     
        store = StoreModel(**store_data) # parse the store data from the user to StoreModel object. (doesnt save to db yet)
        # try to access the db and add the store. any issues that will be raised will also be caught
        try:
            # we will get the ID of the store and check uniquness of columns only when we save it to the db.
            db.session.add(store) # add the store but not saved to the db
            db.session.commit() # save to db
        except IntegrityError: # violation of the name because the name is unique
            abort(400, message="A store with that name already exists")
        except SQLAlchemyError:
            abort(500, message="An error occurred while creating the store")

        return store
    
# Use methodview to create class that his methodes route to specific endpoints
@blp.route("/store/<int:store_id>")
class Store(MethodView):

    # we want a get request from /store/store_id to be routed to this function
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id) # query for the store by its id, if it doesnt exist, return 404
        return store
    
    # we want a delete request from /store/store_id to be routed to this function
    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message": "Store deleted"}

