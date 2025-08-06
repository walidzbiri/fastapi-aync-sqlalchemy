from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

from app.db import Base, engine
from app import crud, schemas

from app.deps import SessionDep


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)


@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: SessionDep):
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user=await crud.create_user(db=db, user=user)
    return schemas.User.model_validate(db_user)


@app.get("/users/", response_model=list[schemas.User])
async def read_users(
    db: SessionDep, skip: int = 0, limit: int = 100
):
    db_users=await crud.get_users(db, skip=skip, limit=limit)
    return [schemas.User.model_validate(db_user) for db_user in db_users]


@app.get("/users/{user_id}", response_model=schemas.User)
async def read_user(db: SessionDep, user_id: int):
    db_user = await crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.User.model_validate(db_user)


@app.delete("/users/{user_id}")
async def delete_user(db: SessionDep, user_id: int):
    return await crud.delete_user(db, user_id=user_id)


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
async def create_item_for_user(
    db: SessionDep, user_id: int, item: schemas.ItemCreate,
):
    return await crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
async def read_items(
    db: SessionDep, skip: int = 0, limit: int = 100
):
    db_items= await crud.get_items(db, skip=skip, limit=limit)
    return [schemas.Item.model_validate(db_item) for db_item in db_items]
