import httpx
from fastapi import APIRouter, HTTPException, Request

from auth import hash_password
from models import AccountCreate, AccountResponse, LoginRequest, LoginFeedback
from database import get_user, create_user
from auth import verify_password

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
    response = await create_user(pool, email, username, hashed_password)

    return AccountResponse(status="ok", userid=response)


@router.post("/login", response_model=LoginFeedback)
async def login(
    body: LoginRequest,
    request: Request
) -> LoginFeedback:

    pool = request.app.state.pool

    username = body.username
    password = body.password

    if not username:
        raise HTTPException(
            status_code=400,
            detail="No username provided!"
        )

    if not password:
        raise HTTPException(
            status_code=400,
            detail="No password provided!"
        )

    user = await get_user(pool, username)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password!"
        )

    if not verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password!"
        )

    return LoginFeedback(
        status=True,
        id=user["id"]
    )