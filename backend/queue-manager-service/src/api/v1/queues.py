import uuid
from typing import Annotated
from http import HTTPStatus

from fastapi import APIRouter, Depends, Header, HTTPException

from services.queue import QueueService, get_queue_service
from schemas.entity import FilmTogether
from .auth import security_jwt


router = APIRouter()


@router.post(
    '/film_together',
    summary='Поиск пользователей для просмотра конкретного фильма вместе',
    description='Добавление пользователя в существующую очередь или создание новой',
    response_description='-',
)
async def manage_queue(
    film_id: uuid.UUID,
    user_data: Annotated[dict, Depends(security_jwt)],
    user_agent: Annotated[str | None, Header()] = None,
    queue_service: QueueService = Depends(get_queue_service),
) -> None:
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

    await queue_service.handle_queue(
        FilmTogether(
            film_id=film_id,
            user_id=user_data.get('user_id'),
            user_agent=user_agent
        )
    )
