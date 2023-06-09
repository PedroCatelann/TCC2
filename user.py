from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id_users = db.Column(db.Integer, autoincrement = True, primary_key = True)
    name = db.Column(db.String(45), nullable = False)
    email = db.Column(db.String(45), nullable = False)
    password = db.Column(db.String(150), nullable = False)
    user_type = db.Column(db.String(45), nullable = False)

    def __init__(self, name, email, password,user_type):
        self.name = name
        self.email = email
        # self.password = generate_password_hash(password)
        self.password = password
        self.user_type = user_type

    

    def verify_password(self, password):
        return check_password_hash(self.password, password)


