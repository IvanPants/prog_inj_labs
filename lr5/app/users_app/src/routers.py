import hashlib
from datetime import datetime, timedelta

# from models import User

import json
import jwt
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from loguru import logger
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

# from .crud_operations import *
# import crud_operations as crud
from . import crud_operations as crud
from .database import SessionLocal
from .generate_users import generate_users
from .schemas import UserSchema
import redis

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


_redis = redis.Redis(host='redis', port=6379, db=0)

def check_user_token(auth: str = Header(...)):
    print(f'auth: {auth}')
    print(f'test split: {auth.split(".")}')
    payload = jwt.decode(auth, "Well_Done", algorithms=["HS256"])
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=402, detail="Invalid authentication credentials")

    return user_id


@router.post("/post_random_users/{count}")
async def post_random_users(count: int, db: Session = Depends(get_db)):
    users = generate_users(count)
    logger.debug(f'users count: {len(users)}')
    for user in users:
        logger.trace(f'Adding user: {user}')
        crud.add_new_user(db, user)

    return JSONResponse(content={"message": f"{count} users generated and added to db!"})


@router.post("/add")
async def create_user(request: UserSchema, db: Session = Depends(get_db)):
    crud.add_new_user(db, user=request)

    return {
        "message"    : f"user {request.login} successfully added",
        "user"       : request,
        "status_code": "200"
    }


@router.get("/get_by_first_name")
async def get_user_by_first_name(request: str, db: Session = Depends(get_db)):
    key = f'get_by_first_name: {request}'
    redis_search = _redis.lrange(key, 0, -1)
    if redis_search:
        print(f"redis work")
        return {
            "message": f"user '{redis_search}' found in Redis",
            "status_code": "200"
        }
    _user = crud.get_user_by_first_name(db, first_name=request)
    _redis.rpush(key, _user.first_name)
    _redis.rpush(key, _user.second_name)
    _redis.expire(key, 15)

    return {
        "message"    : f"user '{_user.first_name}' found in postgres",
        "user"       : _user,
        "status_code": "200"
    }


@router.get("/get_by_second_name")
async def get_by_second_name(request: str, db: Session = Depends(get_db)):
    key = f'get_by_second_name: {request}'
    redis_search = _redis.lrange(key, 0, -1)
    if redis_search:
        print(f"redis work")
        return {
            "message": f"user '{redis_search}' found in Redis",
            "status_code": "200"
        }

    _user = crud.get_user_by_second_name(db, second_name=request)
    _redis.rpush(key, _user.second_name)
    _redis.expire(key, 15)

    return {
        "message"    : f"user '{_user.second_name}' found in postgres",
        "user"       : _user,
        "status_code": "200"
    }


@router.get("/get_all")
async def get_all(start: int, end: int, db: Session = Depends(get_db)):
    key = f'get_all?start={start}&end={end}'
    redis_search =_redis.lrange(key, 0, -1)
    # hash = key
    if redis_search:
        return f"redis_search {redis_search}"

    _users = crud.get_user(db, skip=start, limit=end)

    _redis.rpush(key,  *[str(u.id) for u in _users])
    _redis.expire(key, 15)

    return {
        "message"    : f"users found",
        "users"      : _users,
        "status_code": "200"
    }


@router.get("/get_user_bu_id")
async def get_all(user_id: int, db: Session = Depends(get_db)):
    key = f'get_user_bu_id: {user_id}'
    redis_search = _redis.lrange(key, 0, -1)
    if redis_search:
        return {
            "message": f"user '{redis_search}' found in Redis",
            "status_code": "200"
        }
    _user = crud.get_user_by_id(db, user_id)

    _redis.rpush(key, (_user.id))
    _redis.expire(key, 15)

    return _user


@router.patch("/update")
async def update_user(user_id: int, new_first_name: str, new_second_name: str,
                      new_password: str, new_login: str, db: Session = Depends(get_db),
                      token_id=Depends(check_user_token)):
    if user_id != token_id:
        raise HTTPException(status_code=402, detail='Bad token')

    _user = crud.update_user(db, user_id=user_id, first_name=new_first_name, second_name=new_second_name,
                             password=new_password, login=new_login)
    return {
        "message"    : f"user {user_id} update",
        "users"      : _user,
        "status_code": "200"
    }


@router.delete("/delete")
async def delete_user(user_id: int, db: Session = Depends(get_db), token_id=Depends(check_user_token)):
    if user_id != token_id:
        raise HTTPException(status_code=402, detail='Bad token')

    _user = crud.remove_user(db, user_id=user_id)

    return {
        "message"    : f"user {user_id} removed",
        "status_code": "200"
    }


@router.post("/login")
async def login(creds: HTTPBasicCredentials = Depends(HTTPBasic()), db: Session = Depends(get_db)):
    _user = crud.get_user_by_login(db, creds.username)
    # raise HTTPException(status_code=402, detail='Bad token')

    if _user is None:
        raise HTTPException(status_code=401, detail="user not found")

    if _user.login != creds.username:
        raise HTTPException(status_code=401, detail="wrong login")
    print(_user.login)

    # print(f'going to use password to hash: {}')
    hash_password = hashlib.sha256(creds.password.encode()).hexdigest()
    print(hash_password)
    if hash_password != _user.password:
        raise HTTPException(status_code=401, detail="wrong password")

    exp_date = datetime.now() + timedelta(minutes=15)

    token_data = {"sub": _user.id, "exp": exp_date}
    token = jwt.encode(token_data, "Well_Done", algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}
