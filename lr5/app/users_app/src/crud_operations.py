import hashlib

from sqlalchemy.orm import Session

from .models import User
from .schemas import UserSchema


def get_user(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def get_user_by_first_name(db: Session, first_name: str):
    return db.query(User).filter(User.first_name == first_name).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_second_name(db: Session, second_name: str):
    return db.query(User).filter(User.second_name == second_name).first()


def get_user_by_login(db: Session, login: str):
    return db.query(User).filter(User.login == login).first()


def add_new_user(db: Session, user: UserSchema):
    hash_password = hashlib.sha256(user.password.encode()).hexdigest()
    print(hash_password)

    _user = User(first_name=user.first_name, second_name=user.second_name, password=hash_password, login=user.login)
    db.add(_user)
    db.commit()
    db.refresh(_user)

    return _user


def remove_user(db: Session, user_id: int):
    _user = get_user_by_id(db=db, user_id=user_id)
    db.delete(_user)
    db.commit()


def update_user(db: Session, user_id: int, first_name: str, second_name: str, password: str, login: str):
    _user = get_user_by_id(db=db, user_id=user_id)

    hash_password = hashlib.sha256(password.encode()).hexdigest()
    _user.first_name = first_name
    _user.second_name = second_name
    _user.password = hash_password
    _user.login = login

    db.commit()
    db.refresh(_user)
    return _user
