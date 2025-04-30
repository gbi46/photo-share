from passlib.context import CryptContext

class Security:
    def __init__(self, schemes=["bcrypt"]):
        self.pwd_context = CryptContext(schemes=schemes, deprecated="auto")

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
    
security = Security()