import uuid
import time
import jwt

from typing import Annotated
from fastapi import (
    APIRouter, WebSocket, WebSocketException, Query, status, Depends
)
from core.config import settings
from services.websocket import WebSocketConnectionService, get_websocket_connection_service


router = APIRouter()


async def decode_token(token: Annotated[str, Query()]) -> dict:
    try:
        decoded_token = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        return decoded_token if decoded_token["exp"] >= time.time() else None
    except jwt.ExpiredSignatureError:
        raise WebSocketException(
            code=status.WS_1007_INVALID_FRAME_PAYLOAD_DATA, reason="Incorrect signature"
        )
    except jwt.InvalidTokenError:
        raise WebSocketException(
            code=status.WS_1009_INVALID_TOKEN, reason="Invalid token"
        )


@router.websocket("/ws/{party_id}")
async def part_connection(
    party_id: uuid.UUID,
    user_data: Annotated[dict, Depends(decode_token)],
    websocket: WebSocket,
    websocket_connection_service: Annotated[
        WebSocketConnectionService, Depends(get_websocket_connection_service)
    ]
):
    await websocket_connection_service.connect(
        user_data["username"], party_id, websocket
    )
