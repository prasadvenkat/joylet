from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    email_verified = Column(Boolean, default=False)
    password_hash = Column(Text, nullable=False)
    display_name = Column(String(40), nullable=False)
    handle = Column(String(30), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    posts = relationship("Post", back_populates="author", foreign_keys="Post.author_id")
    sessions = relationship("Session", back_populates="user")
    likes = relationship("Like", back_populates="user")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(Text, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    body = Column(String(140), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=True)
    positivity_score = Column(String, nullable=True)  # For future ML
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        CheckConstraint('char_length(body) <= 140', name='body_length_check'),
        Index('ix_posts_author_created', 'author_id', 'created_at'),
        Index('ix_posts_parent_id', 'parent_id', postgresql_where=Column('parent_id').isnot(None)),
    )
    
    # Relationships
    author = relationship("User", back_populates="posts", foreign_keys=[author_id])
    likes = relationship("Like", back_populates="post")
    replies = relationship("Post", remote_side=[id])

class Like(Base):
    __tablename__ = "likes"
    
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    post = relationship("Post", back_populates="likes")
    user = relationship("User", back_populates="likes")

class ModerationReport(Base):
    __tablename__ = "moderation_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False, index=True)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="open")  # open, dismissed, actioned

class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"
    
    token = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
