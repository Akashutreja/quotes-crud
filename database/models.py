from .db import db

class Quote(db.Document):
    quote = db.StringField(required=True)
    author = db.StringField(required=True)
    rating = db.IntField()
    addedBy = db.StringField(required=True)
    def to_json(self):
        return {
        			"id": str(self.pk),
                	"quote": self.quote,
                	"rating": self.rating,
                	"addedBy": self.addedBy
                }