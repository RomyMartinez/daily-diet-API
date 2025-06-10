from database import db
from flask_login import UserMixin

class Meal(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(180), nullable = False)
    date = db.Column(db.String(180), nullable = False)
    isDiet = db.Column(db.Boolean, nullable = False)