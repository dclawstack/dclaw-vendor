from fastapi import APIRouter, Depends

from app.core.auth import AuthUser, auth_config, current_user

router = APIRouter()


@router.get("/config")
async def get_auth_config():
    """Public: lets the frontend know whether/how to run the Logto login flow."""
    return auth_config()


@router.get("/me")
async def me(user: AuthUser = Depends(current_user)):
    return {"sub": user.sub, "email": user.email, "anonymous": user.anonymous}
