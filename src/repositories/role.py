from sqlalchemy import insert
from sqlalchemy.future import select
from src.database.models import Permission, Role, role_permissions
from src.services.utils import logger
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_default_permissions(self):
        user_permissions = []

        moderator_permissions = user_permissions + [
            'update_all_posts',
            'delete_all_comments'
        ]

        admin_permissions = moderator_permissions + [
            'delete_all_posts'
        ]

        return {
            'user': user_permissions,
            'moderator': moderator_permissions,
            'admin': admin_permissions
        }
    
    async def get_role_by_name(self, role_name: str):
        role_result = await self.db.execute(select(Role).where(Role.name == role_name))
        return role_result.scalar_one_or_none()
    
    async def create_role(self, role_name: str):
        existing_role = await self.get_role_by_name(role_name)
        if not existing_role:
            new_role = Role(name=role_name)
            self.db.add(new_role)
            await self.db.commit()
            await self.db.refresh(new_role)
            await self.create_role_permissions(new_role.name)
            return new_role
        return existing_role

    async def create_role_permissions(self, role_name):
        permissions_map = await self.get_default_permissions()
        default_permissions = permissions_map.get(role_name, [])

        if not default_permissions:
            return

        role = await self.get_role_by_name(role_name)

        if not role:
            await self.create_role(role_name)
            role = await self.get_role_by_name(role_name)
        
        if not role:
            logger.info(f"Error: Could not retrieve role '{role_name}' after creation.")
            return
       
        for permission_name in default_permissions:
            permission_result = await self.db.execute(
                select(Permission).where(Permission.name == permission_name)
            )
            permission = permission_result.scalar_one_or_none()
            if not permission:
                new_permission = Permission(name=permission_name)
                self.db.add(new_permission)
                await self.db.flush()
                permission = new_permission

            logger.info(f"Checking permission link for role.id={role.id} ({type(role.id)}), permission.id={permission.id} ({type(permission.id)})")

            # Defensive guard
            if not isinstance(role.id, (int, str, UUID)) or not isinstance(permission.id, (int, str, UUID)):
                logger.error(f"Invalid types — role: {role} ({type(role)}), permission: {permission} ({type(permission)})")
                return


            role_permission_exists_result = await self.db.execute(
                select(role_permissions)
                .where(role_permissions.c.role_id == role.id)
                .where(role_permissions.c.permission_id == permission.id)
            )
            role_permission_exists = role_permission_exists_result.scalar_one_or_none()

            if not role_permission_exists:
                insert_stmt = insert(role_permissions).values(
                    role_id=role.id, permission_id=permission.id
                )
                await self.db.execute(insert_stmt)
            
        await self.db.commit()
