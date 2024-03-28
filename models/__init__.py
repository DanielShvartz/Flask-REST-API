# instead of doing (from models.store import storemodel) in another file we just do (from models import storemodel)
from models.store import StoreModel
from models.item import ItemModel
from models.tag import TagModel
from models.item_tag_junction import ItemTagModel
from models.user import UserModel
from models.blocklist import BlocklistModel