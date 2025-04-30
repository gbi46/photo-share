from datetime import datetime
from uuid import uuid4, UUID
from sqlalchemy import Column, DateTime, Enum, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship, declarative_base, Mapped, mapped_column

import enum

Base = declarative_base()

# Association Tables
user_roles = Table(
    'user_roles', Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('role_id', ForeignKey('roles.id'), primary_key=True)
)

role_permissions = Table(
    'role_permissions', Base.metadata,
    Column('role_id', ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', ForeignKey('permissions.id'), primary_key=True)
)

class UserStatusEnum(str, enum.Enum):
    active = "active"
    ban = "ban"

# Models
class User(Base):
    __tablename__ = 'users'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    img_link: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[bool] = mapped_column(Enum(UserStatusEnum), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    roles = relationship('Role', secondary=user_roles, back_populates='users')
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="user")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="user")
    ratings: Mapped[list["PostRating"]] = relationship("PostRating", back_populates="user")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship("RefreshToken", back_populates="user")

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    permissions = relationship('Permission', secondary=role_permissions, back_populates='roles')
    users = relationship('User', secondary=user_roles, back_populates='roles')

class Permission(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    roles = relationship('Role', secondary=role_permissions, back_populates='permissions')

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    user: Mapped["User"] = relationship("User", back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post")
    tags: Mapped[list["PostTag"]] = relationship("PostTag", back_populates="post")
    ratings: Mapped[list["PostRating"]] = relationship("PostRating", back_populates="post")

class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    post_id: Mapped[UUID] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    message: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    user: Mapped["User"] = relationship("User", back_populates="comments")
    post: Mapped["Post"] = relationship("Post", back_populates="comments")

class PostRating(Base):
    __tablename__ = "post_ratings"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    post_id: Mapped[UUID] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    rating: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="ratings")
    post: Mapped["Post"] = relationship("Post", back_populates="ratings")

class PostTag(Base):
    __tablename__ = "post_tags"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    post_id: Mapped[UUID] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    tag_name: Mapped[str] = mapped_column(ForeignKey("tags.name", ondelete="CASCADE"))

    post: Mapped["Post"] = relationship("Post", back_populates="tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="post_tags")

class Tag(Base):
    __tablename__ = "tags"
    name: Mapped[str] = mapped_column(String, primary_key=True)

    post_tags: Mapped[list["PostTag"]] = relationship("PostTag", back_populates="tag")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None
