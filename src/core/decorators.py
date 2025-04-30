from fastapi import Depends, HTTPException, status
from functools import wraps
from src.services.auth import get_current_user

def require_role(role_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, user=Depends(get_current_user), **kwargs):
            if not any(role.name == role_name for role in user.roles):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_permission(permission_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, user=Depends(get_current_user), **kwargs):
            if not any(permission_name in [p["name"] for p in role.permissions] for role in user.roles):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing permission.")
            return func(*args, **kwargs)
        return wrapper
    return decorator
