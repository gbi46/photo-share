from src.database.models import User
from src.services.auth import get_current_user
from fastapi import Depends, HTTPException, status
from functools import wraps

def require_role(role_name: str):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if not any(role.name == role_name for role in current_user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: insufficient role",
            )
        return current_user
    return Depends(role_checker)

def require_permission(permission_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, user=Depends(get_current_user), **kwargs):
            if not any(permission_name in [p["name"] for p in role.permissions] for role in user.roles):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing permission.")
            return func(*args, **kwargs)
        return wrapper
    return decorator
