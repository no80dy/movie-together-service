import uuid
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Header, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from schemas.entity import FilmTogether
from services.queue import QueueService, get_queue_service

from .auth import security_jwt

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.post(
    "/film_together",
    summary="Поиск пользователей для просмотра конкретного фильма вместе",
    description="Добавление пользователя в существующую очередь или создание новой",
    response_description="Перенаправление на страницу ожидания",
)
async def manage_queue(
    request: Request,
    user_data: Annotated[dict, Depends(security_jwt)],
    film_id: uuid.UUID = Form(),
    user_agent: Annotated[str | None, Header()] = None,
    queue_service: QueueService = Depends(get_queue_service),
):
    """
    Пользователь, который хочет посмотреть фильм, добавляется в очередь ожидания.
    При наборе определенного количества пользователей для данной группы пользователей
    отправляется запрос на создание сеанса просмотра.
    """
    if not user_agent:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Вы пытаетесь зайти с неизвестного устройства",
        )

    film_together = FilmTogether(
        film_id=film_id,
        user_id=user_data.get("user_id"),
        user_agent=user_agent,
    )

    if await queue_service.check_if_client_id_exist(film_together):
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Данный пользователь уже ожидает начало совместного просмотра данного фильма с данного устройства ",
        )

    client_id = await queue_service.handle_queue(film_together)
    if client_id:
        return templates.TemplateResponse(
            name="waiting_party.html",
            context={
                "request": request,
                "client_id": client_id,
            }
        )
    else:
        RedirectResponse('/start')


@router.get(
    '/start',
    summary="Ожидание начала показа фильма",
)
async def start(
    request: Request,
    user_data: Annotated[dict, Depends(security_jwt)],
):
    return templates.TemplateResponse(
        name="loading.html",
        context={
            "request": request,
        }
    )
