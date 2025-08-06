from fastapi import HTTPException
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas


async def get_user(db: AsyncSession, user_id: int):
    return await db.get(models.User, user_id)


async def get_user_by_email(db: AsyncSession, email: str):
    query = select(models.User).where(email==email)
    result = await db.execute(query)
    return result.one_or_none()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    query = (
            select(models.User)
            .offset(skip)
            .limit(limit)
        )
    result = await db.execute(query)
    return result.scalars().all()


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user=models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int):
    db_user=await db.get(models.User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(db_user)
    await db.commit()


async def get_items(db: AsyncSession, skip: int = 0, limit: int = 100):
    query = (
            select(models.Item)
            .offset(skip)
            .limit(limit)
        )
    result = await db.execute(query)
    return result.scalars().all()

async def create_user_item(db: AsyncSession, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.model_dump(), owner_id=user_id)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item