from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, logout_user, LoginManager

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id_users = db.Column(db.Integer, autoincrement = True, primary_key = True)
    name = db.Column(db.String(45), nullable = False)
    email = db.Column(db.String(45), nullable = False)
    password = db.Column(db.String(150), nullable = False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        # self.password = generate_password_hash(password)
        self.password = password

    

    def verify_password(self, password):
        return check_password_hash(self.password, password)


