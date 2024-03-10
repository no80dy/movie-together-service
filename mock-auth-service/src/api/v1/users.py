import logging
from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from core.config import JWTSettings
from db.users import users_db
from fastapi import (
    APIRouter,
    Body,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Request,
)
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer
from fastapi.templating import Jinja2Templates
from models.models import User
from services.user import UserService, get_user_service

security = HTTPBearer()
router = APIRouter()


# Настройки модуля async_fastapi_jwt_auth
@AuthJWT.load_config
def get_config():
    return JWTSettings()


templates = Jinja2Templates(directory="templates")


@router.get(
    path="/login",
    status_code=HTTPStatus.OK,
    response_class=HTMLResponse,
    description="Mock frontend login page",
)
async def login(
    request: Request,
    Authorize: AuthJWT = Depends(),
):
    await Authorize.jwt_optional()
    authorized = await Authorize.get_jwt_subject()
    if authorized:
        user_claims = await Authorize.get_raw_jwt()
        return templates.TemplateResponse(
            name="loading.html",
            context={
                "request": request,
                "user_id": user_claims['user_id'],
            },
        )
    else:
        return templates.TemplateResponse(
            name="login.html",
            context={
                "request": request,
            },
        )


@router.post(
    path="/signin",
    status_code=HTTPStatus.OK,
    summary="Вход пользователя в аккаунт",
    description="На основании логина и пароля формирует пару access и refresh токенов",
    response_description="Аутентификация пользователя по логину и паролю",
)
async def signin(
    request: Request,
    username: str = Form(),
    password: str = Form(),
    user_service: UserService = Depends(get_user_service),
    Authorize: AuthJWT = Depends(),
):
    """Вход пользователя в аккаунт."""
    # проверяем валидность имени пользователя и пароля
    user = await user_service.check_user_exist(username, password)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
        )

    user_claims = {
        "username": user.username,
        "user_id": str(user.user_id),
    }

    # создаем пару access и refresh токенов
    access_token = await Authorize.create_access_token(
        subject=user.username, user_claims=user_claims
    )
    refresh_token = await Authorize.create_refresh_token(
        subject=user.username, user_claims=user_claims
    )

    response = templates.TemplateResponse(
        name="loading.html",
        context={
            "request": request,
            "user_id": user_claims['user_id'],
        },
    )

    # Set the JWT cookies in the response
    await Authorize.set_access_cookies(access_token, response)
    await Authorize.set_refresh_cookies(refresh_token, response)

    return response


@router.get("/logout")
async def logout(request: Request, Authorize: AuthJWT = Depends()):
    await Authorize.jwt_required()
    response = templates.TemplateResponse(
        name="login.html",
        context={
            "request": request,
        },
    )
    await Authorize.unset_jwt_cookies(response)
    return response


@router.get("/protected")
async def protected(Authorize: AuthJWT = Depends()):
    await Authorize.jwt_optional()
    # If no jwt is sent in the request, get_jwt_subject() will return None
    username = await Authorize.get_jwt_subject()
    return {"username": username}


@router.post(
    path="/film_together",
    status_code=HTTPStatus.OK,
    summary="Страница совместного просмотра фильма",
)
async def film_together(
    request: Request,
    film_id: str = Form(),
    Authorize: AuthJWT = Depends(),
):
    """Страница выбора фильма для совместного просмотра."""
    await Authorize.jwt_required()

    return JSONResponse(content={"msg": film_id})
