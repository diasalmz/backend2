from fastapi import APIRouter, Depends
from app.models.user import User as UserModel
from app.api import deps
from app.schemas.user import User as UserSchema

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def read_users_me(
    current_user: UserModel = Depends(deps.get_current_user),
):
    """
    Get current user from in-memory store.
    """
    # Так как get_current_user теперь возвращает MockUser,
    # а response_model ожидает схему Pydantic,
    # FastAPI автоматически преобразует их, если поля совпадают.
    return current_user