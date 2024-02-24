# from typing import Annotated
#
# from fastapi import APIRouter, Depends
# from schemas.websocket import InputLikeCommentMessage
# from services.websocket import WebSocketService, get_websocket_service
#
# router = APIRouter()
#
#
# @router.post(
#     "/like",
#     summary="Отправка события о лайке в воркер",
#     description="Публикация в RabbitMQ и запись в MongoDB нотификации",
#     response_description="Информация о нотификации",
# )
# async def handle_likes(
#     message: InputLikeCommentMessage,
#     websocket_service: Annotated[WebSocketService, Depends(get_websocket_service)],
# ):
#     await websocket_service.handle_message(message.model_dump())
