import httpx
from fastapi import APIRouter, HTTPException, Request

from auth import hash_password
from models import AccountCreate, AccountResponse
from database import get_user, create_user

router = APIRouter()


@router.post("/create", response_model=AccountResponse)
async def create_account(body: AccountCreate, request: Request) -> AccountResponse:
    pool = request.app.state.pool

    email = body.email
    username = body.username
    password = body.password

    user = await get_user(pool, body.username)
    if user is not None:
        raise HTTPException(status_code=401, detail="User with this name already exists!")
    if password is None:
        raise HTTPException(status_code=401, detail="No password provided!")

    hashed_password = hash_password(password)
    print(password)
    response = await create_user(pool, email, username, hashed_password)
    print(response, hashed_password)

    return AccountCreate(status="ok", userid=response)
