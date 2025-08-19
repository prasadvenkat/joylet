from fastapi import FastAPI, Depends, HTTPException, status, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, and_, or_
from contextlib import asynccontextmanager
import uuid
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, List
import re
import json

from database import get_db, init_db
from models import User, Post, Like, Session, EmailVerificationToken, ModerationReport
from schemas import *

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database
    await init_db()
    yield

app = FastAPI(
    title="Positive Micro-Journal API",
    description="A platform for sharing positive micro-posts",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://joylet-frontend.onrender.com",
        "https://*.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple profanity filter
NEGATIVE_WORDS = [
    "hate", "stupid", "idiot", "awful", "terrible", "horrible", 
    "sucks", "worst", "fail", "loser", "pathetic"
]

def check_positivity(text: str) -> bool:
    """Basic rule-based positivity check"""
    text_lower = text.lower()
    
    # Check for negative words
    for word in NEGATIVE_WORDS:
        if word in text_lower:
            return False
    
    # Check for excessive negativity patterns
    negative_patterns = [
        r"\b(not|never|can't|won't|don't|couldn't|shouldn't)\b.*\b(good|great|amazing|awesome)\b",
        r"\b(everything|nothing).*\b(wrong|bad|terrible)\b"
    ]
    
    for pattern in negative_patterns:
        if re.search(pattern, text_lower):
            return False
    
    return True

# Dependency to get current user
async def get_current_user(
    session_token: Optional[str] = Cookie(None, alias="session"),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    if not session_token:
        return None
    
    # Query session and user
    stmt = select(Session).options(selectinload(Session.user)).where(
        and_(
            Session.token_hash == session_token,
            Session.expires_at > datetime.utcnow(),
            Session.revoked == False
        )
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        return None
    
    return session.user

async def require_auth(current_user: User = Depends(get_current_user)) -> User:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return current_user

# Auth endpoints
@app.post("/auth/register", response_model=MessageResponse)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    try:
        print(f"Registration attempt - Email: {user_data.email}, Display name: {user_data.display_name}")
        
        # Check if user exists
        stmt = select(User).where(User.email == user_data.email)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"User already exists: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user with bcrypt password hashing
        print("Hashing password...")
        hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        print("Creating user object...")
        user = User(
            email=user_data.email,
            password_hash=hashed_password,
            display_name=user_data.display_name,
            handle=user_data.display_name.lower().replace(" ", "_")[:30],
            email_verified=True  # Auto-verify for local testing
        )
        
        print(f"Adding user to database: {user.email}")
        db.add(user)
        
        print("Committing to database...")
        await db.commit()
        
        print("Refreshing user object...")
        await db.refresh(user)
        
        print(f"User created successfully with ID: {user.id}")
        
        return MessageResponse(message="Registration successful! You can now log in.")
        
    except HTTPException:
        # Re-raise HTTP exceptions (like "email already exists")
        raise
    except Exception as e:
        print(f"Unexpected error during registration: {type(e).__name__}: {str(e)}")
        print(f"Error details: {repr(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/auth/verify-email", response_model=MessageResponse)
async def verify_email(request: EmailVerification, db: AsyncSession = Depends(get_db)):
    stmt = select(EmailVerificationToken).where(
        and_(
            EmailVerificationToken.token == request.token,
            EmailVerificationToken.expires_at > datetime.utcnow()
        )
    )
    result = await db.execute(stmt)
    token = result.scalar_one_or_none()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    # Update user
    user_stmt = select(User).where(User.id == token.user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one()
    user.email_verified = True
    
    # Delete token
    await db.delete(token)
    await db.commit()
    
    return MessageResponse(message="Email verified successfully")

@app.post("/auth/login")
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    # Find user
    stmt = select(User).where(User.email == credentials.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password with bcrypt
    if not bcrypt.checkpw(credentials.password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please verify your email first"
        )
    
    # Create session
    session_token = str(uuid.uuid4())
    session = Session(
        user_id=user.id,
        token_hash=session_token,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    
    db.add(session)
    await db.commit()
    
    # Create proper JSON response
    from fastapi import Response
    
    response_data = {
        "message": "Login successful",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "display_name": user.display_name,
            "handle": user.handle
        }
    }
    
    # Create response with cookie
    response = Response(
        content=json.dumps(response_data),
        media_type="application/json"
    )
    response.set_cookie(
        key="session",
        value=session_token,
        httponly=True,
        secure=False,  # Set to False for localhost
        samesite="lax",
        max_age=30 * 24 * 60 * 60  # 30 days
    )
    
    return response

@app.post("/auth/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(require_auth),
    session_token: Optional[str] = Cookie(None, alias="session"),
    db: AsyncSession = Depends(get_db)
):
    if session_token:
        stmt = select(Session).where(Session.token_hash == session_token)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        if session:
            session.revoked = True
            await db.commit()
    
    from fastapi import Response
    resp = Response(content='{"message": "Logged out successfully"}')
    resp.delete_cookie(key="session")
    return resp

# User endpoints
@app.get("/users/me", response_model=UserProfile)
async def get_my_profile(current_user: User = Depends(require_auth)):
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
        handle=current_user.handle,
        created_at=current_user.created_at
    )

@app.get("/users/{user_id}", response_model=PublicUserProfile)
async def get_user_profile(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get post count
    post_count_stmt = select(func.count(Post.id)).where(
        and_(Post.author_id == user_id, Post.is_deleted == False)
    )
    post_count_result = await db.execute(post_count_stmt)
    post_count = post_count_result.scalar()
    
    return PublicUserProfile(
        id=user.id,
        display_name=user.display_name,
        handle=user.handle,
        created_at=user.created_at,
        post_count=post_count
    )

# Post endpoints
@app.get("/posts", response_model=PostList)
async def get_posts(
    cursor: Optional[str] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    # Build query for top-level posts only
    stmt = select(Post).options(selectinload(Post.author)).where(
        and_(Post.parent_id.is_(None), Post.is_deleted == False)
    ).order_by(Post.created_at.desc()).limit(limit + 1)
    
    if cursor:
        # Parse cursor (timestamp_id format)
        try:
            timestamp_str, post_id = cursor.split("_")
            cursor_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            stmt = stmt.where(
                or_(
                    Post.created_at < cursor_time,
                    and_(Post.created_at == cursor_time, Post.id < uuid.UUID(post_id))
                )
            )
        except:
            pass  # Invalid cursor, ignore
    
    result = await db.execute(stmt)
    posts = result.scalars().all()
    
    # Check if there are more posts
    has_more = len(posts) > limit
    if has_more:
        posts = posts[:-1]
    
    # Get like counts and user likes
    post_items = []
    for post in posts:
        # Get like count
        like_count_stmt = select(func.count(Like.post_id)).where(Like.post_id == post.id)
        like_count_result = await db.execute(like_count_stmt)
        like_count = like_count_result.scalar()
        
        # Check if current user liked
        user_liked = False
        if current_user:
            user_like_stmt = select(Like).where(
                and_(Like.post_id == post.id, Like.user_id == current_user.id)
            )
            user_like_result = await db.execute(user_like_stmt)
            user_liked = user_like_result.scalar_one_or_none() is not None
        
        # Get reply count
        reply_count_stmt = select(func.count(Post.id)).where(
            and_(Post.parent_id == post.id, Post.is_deleted == False)
        )
        reply_count_result = await db.execute(reply_count_stmt)
        reply_count = reply_count_result.scalar()
        
        post_items.append(PostResponse(
            id=post.id,
            body=post.body,
            author=UserResponse(
                id=post.author.id,
                display_name=post.author.display_name,
                handle=post.author.handle
            ),
            parent_id=post.parent_id,
            like_count=like_count,
            reply_count=reply_count,
            user_liked=user_liked,
            created_at=post.created_at
        ))
    
    # Generate next cursor
    next_cursor = None
    if has_more and posts:
        last_post = posts[-1]
        next_cursor = f"{last_post.created_at.isoformat()}_{last_post.id}"
    
    return PostList(items=post_items, next_cursor=next_cursor)

@app.post("/posts", response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db)
):
    # Check positivity
    if not check_positivity(post_data.body):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please keep your post positive! Try sharing something you're grateful for or a small win."
        )
    
    # Check if parent exists (for replies)
    if post_data.parent_id:
        parent_stmt = select(Post).where(Post.id == post_data.parent_id)
        parent_result = await db.execute(parent_stmt)
        parent_post = parent_result.scalar_one_or_none()
        if not parent_post:
            raise HTTPException(status_code=404, detail="Parent post not found")
    
    # Create post
    post = Post(
        author_id=current_user.id,
        body=post_data.body,
        parent_id=post_data.parent_id
    )
    
    db.add(post)
    await db.commit()
    await db.refresh(post, ["author"])
    
    return PostResponse(
        id=post.id,
        body=post.body,
        author=UserResponse(
            id=current_user.id,
            display_name=current_user.display_name,
            handle=current_user.handle
        ),
        parent_id=post.parent_id,
        like_count=0,
        reply_count=0,
        user_liked=False,
        created_at=post.created_at
    )

@app.get("/posts/{post_id}", response_model=PostDetail)
async def get_post_detail(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    # Get main post
    stmt = select(Post).options(selectinload(Post.author)).where(Post.id == post_id)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Get like count and user like status
    like_count_stmt = select(func.count(Like.post_id)).where(Like.post_id == post.id)
    like_count_result = await db.execute(like_count_stmt)
    like_count = like_count_result.scalar()
    
    user_liked = False
    if current_user:
        user_like_stmt = select(Like).where(
            and_(Like.post_id == post.id, Like.user_id == current_user.id)
        )
        user_like_result = await db.execute(user_like_stmt)
        user_liked = user_like_result.scalar_one_or_none() is not None
    
    # Get replies
    replies_stmt = select(Post).options(selectinload(Post.author)).where(
        and_(Post.parent_id == post_id, Post.is_deleted == False)
    ).order_by(Post.created_at.asc())
    
    replies_result = await db.execute(replies_stmt)
    replies = replies_result.scalars().all()
    
    reply_items = []
    for reply in replies:
        # Get reply like count
        reply_like_count_stmt = select(func.count(Like.post_id)).where(Like.post_id == reply.id)
        reply_like_count_result = await db.execute(reply_like_count_stmt)
        reply_like_count = reply_like_count_result.scalar()
        
        # Check if user liked reply
        reply_user_liked = False
        if current_user:
            reply_user_like_stmt = select(Like).where(
                and_(Like.post_id == reply.id, Like.user_id == current_user.id)
            )
            reply_user_like_result = await db.execute(reply_user_like_stmt)
            reply_user_liked = reply_user_like_result.scalar_one_or_none() is not None
        
        reply_items.append(PostResponse(
            id=reply.id,
            body=reply.body,
            author=UserResponse(
                id=reply.author.id,
                display_name=reply.author.display_name,
                handle=reply.author.handle
            ),
            parent_id=reply.parent_id,
            like_count=reply_like_count,
            reply_count=0,  # No nested replies for now
            user_liked=reply_user_liked,
            created_at=reply.created_at
        ))
    
    main_post = PostResponse(
        id=post.id,
        body=post.body if not post.is_deleted else "[Post removed by author]",
        author=UserResponse(
            id=post.author.id,
            display_name=post.author.display_name,
            handle=post.author.handle
        ) if not post.is_deleted else None,
        parent_id=post.parent_id,
        like_count=like_count,
        reply_count=len(reply_items),
        user_liked=user_liked,
        created_at=post.created_at
    )
    
    return PostDetail(post=main_post, replies=reply_items)

@app.delete("/posts/{post_id}", response_model=MessageResponse)
async def delete_post(
    post_id: uuid.UUID,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Post).where(Post.id == post_id)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    post.is_deleted = True
    await db.commit()
    
    return MessageResponse(message="Post deleted successfully")

# Like endpoints
@app.post("/posts/{post_id}/like", response_model=LikeResponse)
async def toggle_like(
    post_id: uuid.UUID,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db)
):
    # Check if post exists
    post_stmt = select(Post).where(Post.id == post_id)
    post_result = await db.execute(post_stmt)
    post = post_result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user already liked
    like_stmt = select(Like).where(
        and_(Like.post_id == post_id, Like.user_id == current_user.id)
    )
    like_result = await db.execute(like_stmt)
    existing_like = like_result.scalar_one_or_none()
    
    if existing_like:
        # Unlike
        await db.delete(existing_like)
        liked = False
    else:
        # Like
        like = Like(post_id=post_id, user_id=current_user.id)
        db.add(like)
        liked = True
    
    await db.commit()
    
    # Get updated like count
    count_stmt = select(func.count(Like.post_id)).where(Like.post_id == post_id)
    count_result = await db.execute(count_stmt)
    like_count = count_result.scalar()
    
    return LikeResponse(liked=liked, like_count=like_count)

# Admin endpoint for debugging
@app.get("/admin/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    """Debug endpoint to list all users"""
    stmt = select(User)
    result = await db.execute(stmt)
    users = result.scalars().all()
    
    return {
        "total_users": len(users),
        "users": [
            {
                "id": str(user.id),
                "email": user.email,
                "display_name": user.display_name,
                "handle": user.handle,
                "email_verified": user.email_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            for user in users
        ]
    }

# Health check
@app.get("/healthz")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)