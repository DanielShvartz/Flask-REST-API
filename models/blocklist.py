from db import db

class BlocklistModel(db.Model):

    __tablename__ = "blocklist"

    jti = db.Column(db.String(), primary_key=True)
    # We dont need an id, because the jti is unique identifier, so we dont need an id, we can set the jti as our own jti from the JWT.

# We can also add a column from an expiry date, and then check if the expire date is expired, then we can delete this record, because its already not usable.