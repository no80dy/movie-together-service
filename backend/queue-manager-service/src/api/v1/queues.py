import uuid
from typing import Annotated
from http import HTTPStatus

from fastapi import APIRouter, Depends, Header, HTTPException, Form
from fastapi.responses import RedirectResponse, JSONResponse

from services.queue import QueueService, get_queue_service
from schemas.entity import FilmTogether
from .auth import security_jwt


router = APIRouter()


@router.post(
    '/film_together',
    summary='Поиск пользователей для просмотра конкретного фильма вместе',
    description='Добавление пользователя в существующую очередь или создание новой',
    response_description='Перенаправление на страницу ожидания',
)
async def manage_queue(
    film_id: uuid.UUID = Form(),
    # user_data: Annotated[dict, Depends(security_jwt)],
    user_agent: Annotated[str | None, Header()] = None,
    queue_service: QueueService = Depends(get_queue_service),
) -> RedirectResponse:
    """
    Пользователь, который хочет посмотреть фильм, добавляется в очередь ожидания.
    При наборе определенного количества пользователей для данной группы пользователей
    отправляется запрос на создание сеанса просмотра.
    """
    if not user_agent:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Вы пытаетесь зайти с неизвестного устройства'
        )

    # for test
    user_data = {'user_id': '86830a5a-4b8c-4ea3-91f6-a2b6e03bdc50'}

    film_together = FilmTogether(
            film_id=film_id,
            user_id=user_data.get('user_id'),
            user_agent=user_agent
        )

    if await queue_service.check_if_client_id_exist(film_together):
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Данный пользователь уже ожидает начало совместного просмотра данного фильма с данного устройства '
        )

    await queue_service.handle_queue(film_together)
    return RedirectResponse('/waiting_party/api/v1', status_code=HTTPStatus.FOUND)
