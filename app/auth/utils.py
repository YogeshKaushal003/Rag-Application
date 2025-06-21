from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
from app.models.models import User

bcrypt = Bcrypt()

def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.check_password_hash(hashed, password)

def generate_tokens(identity):
    access_token = create_access_token(identity=identity, expires_delta=timedelta(minutes=30))
    refresh_token = create_refresh_token(identity=identity)
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
