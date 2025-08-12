from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, declarative_base, relationship

Base = declarative_base()


class DBUser(Base):
    __tablename__ = "users"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    email: Mapped[str] = Column(String, unique=True, index=True)
    hashed_password: Mapped[str] = Column(String)
    is_active: Mapped[bool] = Column(Boolean, default=True)

    # Lazy is workaround for async, use either "subquery" or "selectin" # noqa
    # More info: https://github.com/tiangolo/fastapi/pull/2331#issuecomment-801461215 and https://github.com/tiangolo/fastapi/pull/2331#issuecomment-807528963
    items: Mapped[list["DBItem"]] = relationship(
        "DBItem", back_populates="owner", lazy="subquery"
    )


class DBItem(Base):
    __tablename__ = "items"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    title: Mapped[str] = Column(String, index=True)
    description: Mapped[str] = Column(String, index=True)
    owner_id: Mapped[int] = Column(Integer, ForeignKey("users.id"))

    owner: Mapped["DBUser"] = relationship("DBUser", back_populates="items")
