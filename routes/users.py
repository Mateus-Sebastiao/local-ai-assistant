from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
import models
import schemas
from core.security import get_password_hash

router = APIRouter()

@router.post("", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: schemas.UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    query = select(models.User).where(
        (models.User.email == user_in.email) | (models.User.username == user_in.username)
    )
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User with this email or username already exists")

    db_user = models.User(
        **user_in.model_dump(exclude={"password"}), 
        hashed_password=get_password_hash(user_in.password)
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.get("", response_model=List[schemas.UserResponse])
async def list_users(db: Annotated[AsyncSession, Depends(get_db)]):
    users = await db.execute(select(models.User)).scalars().all()
    return users

@router.patch("/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: int, 
    user_update: schemas.UserUpdate, 
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Partial update of user details using PATCH.
    """
    db_user = await db.get(models.User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Filter only provided data (exclude_unset=True)
    update_data = user_update.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(db_user, key, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Hard delete of a user record.
    """
    db_user = await db.get(models.User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    await db.commit()
    return None