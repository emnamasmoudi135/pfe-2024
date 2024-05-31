# app/api/userManagement/user.py
import uuid  # pour générer un token unique
from flask import current_app as app
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

class User:
    def __init__(self):
        client = MongoClient(app.config['MONGO_URI'])
        self.db = client[app.config['MONGO_DB_NAME']]
        self.users = self.db.users
        self.login_tokens = self.db.login_tokens

    def create_user(self, username, email, password, role="user"):
        if self.users.find_one({"email": email}):
            return False, "User with this email already exists.", None
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        verification_token = str(uuid.uuid4())
        user = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "role": role,
            "is_email_verified": False,
            "verification_token": verification_token
        }
        self.users.insert_one(user)
        return True, "User created successfully. Please verify your email.", verification_token

    def find_user_by_email(self, email):
        return self.users.find_one({"email": email})

    def verify_password(self, user, password):
        return check_password_hash(user['password'], password)

    def verify_email(self, token):
        user = self.users.find_one({"verification_token": token})
        if user:
            self.users.update_one({"_id": user["_id"]}, {"$set": {"is_email_verified": True}})
            return True
        return False

    def create_login_token(self, email):
        token = str(uuid.uuid4())
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        self.login_tokens.insert_one({"email": email, "token": token, "expires_at": expiration_time})
        return token

    def verify_login_token(self, token):
        token_data = self.login_tokens.find_one({"token": token})
        if token_data and token_data['expires_at'] > datetime.datetime.utcnow():
            user = self.find_user_by_email(token_data['email'])
            return user
        return None
