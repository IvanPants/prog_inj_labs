from sqlalchemy import Column, Integer, String

from .database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    second_name = Column(String)
    password = Column(String)
    login = Column(String, unique=True)
