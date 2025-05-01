from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from src.conf.config import settings
from typing import Any
from uuid import UUID

class Security:
    def __init__(self, schemes=["bcrypt"]):
        self.pwd_context = CryptContext(schemes=schemes, deprecated="auto")

    def create_token(
            self,
            token_type: str,
            subject: str | Any
    ) -> str:
        if token_type == 'access':
            expiration = settings.ACCESS_TOKEN_EXPIRE_MINUTES
            secret_key = settings.SECRET_KEY
        elif token_type == 'refresh':
            expiration = settings.REFRESH_TOKEN_EXPIRE_DAYS
            secret_key = settings.REFRESH_SECRET_KEY

        expire = datetime.now() + timedelta(minutes=expiration)
        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def generate_tokens(self, user_id: UUID) -> dict[str, str]:
        access_token = self.create_token('access', user_id)
        refresh_token = self.create_token('refresh', user_id)
        return {
            "access_token": access_token, 
            "token_type": "bearer", 
            "refresh_token": refresh_token
        }    

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, password: str) -> bool:
        return self.pwd_context.verify(plain_password, password)
    
security = Security()