from src.database.db import get_db 
from src.database.models import Comment, Post, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.services.auth import get_current_user
from src.services.utils import logger
from fastapi import Depends, HTTPException, status
from uuid import UUID

def user_has_access(access_type):
    async def checker(
        post_id: UUID,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ) -> Post:
        stmt = select(Post).where(Post.id == post_id)
        result = await db.execute(stmt)
        post = result.scalar_one_or_none()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # is author
        if post.user_id == user.id:
            return post

        # is has elevated role
        roles = {r.name for r in user.roles}
        if roles.intersection({"admin", "moderator"}):
            return post

        # is has permission
        user_permissions = {
            p.name for r in user.roles for p in r.permissions
        }
        if f"{access_type}_all_posts" in user_permissions:
            return post

        # if no valid permission
        raise HTTPException(status_code=403, detail=f"You cannot {access_type} this post")

    return Depends(checker)

def user_has_access_to_comment(access_type):
    async def checker(
        comment_id: UUID,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ) -> Comment:
        stmt = select(Comment).where(Comment.id == comment_id)
        result = await db.execute(stmt)
        comment = result.scalar_one_or_none()

        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        # is author
        print(f"Comment user id: {comment.user_id}")
        print(f"User id: {user.id}")
        if comment.user_id == user.id:
            return comment

        # is has elevated role
        roles = {r.name for r in user.roles}
        if roles.intersection({"admin", "moderator"}):
            # is has permission
            user_permissions = {
                p.name for r in user.roles for p in r.permissions
            }
            if f"{access_type}_all_comments" in user_permissions:
                return comment

        # if no valid permission
        raise HTTPException(status_code=403, detail=f"You cannot {access_type} this comment")

    return Depends(checker)

def can_view_account():
    async def account_checker(
        account_id: UUID,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
    ):
        stmt = select(User).where(User.id == account_id)
        result = await db.execute(stmt)
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        if account_id == user.id:
            return account
        
        roles = {r.name for r in user.roles}
        if roles.intersection({"admin"}):
            return account
        
        raise HTTPException(status_code=403, detail=f"You cannot view this account")
    
    return Depends(account_checker)

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
    async def checker(user: User = Depends(get_current_user)):
        logger.info(f"Checking permission for user: {user.id}")
        logger.info(f"user.roles: {user.roles} (type={type(user.roles)})")

        for role in user.roles:
            logger.info(f"role: {role.name} (type={type(role)})")
            logger.info(f"permissions: {role.permissions} (type={type(role.permissions)})")

        user_permissions = {
            perm.name
            for role in user.roles
            for perm in role.permissions
        }

        if permission_name not in user_permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Missing permission: {permission_name}"
            )
        return user
    return Depends(checker)
