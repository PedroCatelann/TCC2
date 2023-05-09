from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Visualization(db.Model):
    __tablename__ = "visualization"
    id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    link = db.Column(db.String(150), nullable = False)
    users_id = db.Column(db.Integer, nullable = False)


    def __init__(self, link, users_id):
        self.link = link
        # self.password = generate_password_hash(password)
        self.users_id = users_id


