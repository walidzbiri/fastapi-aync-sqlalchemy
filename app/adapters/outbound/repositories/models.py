from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class DBUser(Base):
    __tablename__ = "users"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    email: Mapped[str] = Column(String, unique=True, index=True)
    hashed_password: Mapped[str] = Column(String)
    is_active: Mapped[bool] = Column(Boolean, default=True)

    items: Mapped[list["DBItem"]] = relationship("DBItem", back_populates="owner")


class DBItem(Base):
    __tablename__ = "items"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    title: Mapped[str] = Column(String, index=True)
    description: Mapped[str] = Column(String, index=True)
    owner_id: Mapped[int] = Column(Integer, ForeignKey("users.id"))

    owner: Mapped["DBUser"] = relationship("DBUser", back_populates="items")
