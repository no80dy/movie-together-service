import time
import uuid
from typing import Annotated

import jwt
from core.config import settings
from fastapi import (
    APIRouter,
    Depends,
    Query,
    WebSocket,
    WebSocketException,
    status,
)
from services.websocket import (
    WebSocketChatConnectionService,
    WebSocketStreamConnectionService,
    get_websocket_chat_connection_service,
    get_websocket_stream_connection_service,
)

router = APIRouter()


async def decode_token(token: Annotated[str, Query()]) -> dict:
    try:
        decoded_token = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        return decoded_token if decoded_token["exp"] >= time.time() else None
    except jwt.ExpiredSignatureError:
        raise WebSocketException(
            code=status.WS_1007_INVALID_FRAME_PAYLOAD_DATA,
            reason="Incorrect signature",
        )
    except jwt.InvalidTokenError:
        raise WebSocketException(
            code=status.WS_1009_INVALID_TOKEN, reason="Invalid token"
        )


@router.websocket("/ws/stream/{party_id}")
async def stream_party_connection(
    party_id: uuid.UUID,
    websocket: WebSocket,
    websocket_stream_connection_service: Annotated[
        WebSocketStreamConnectionService,
        Depends(get_websocket_stream_connection_service),
    ],
):
    await websocket_stream_connection_service.connect(party_id, websocket)


@router.websocket("/ws/chat/{party_id}")
async def chat_party_stream_connection(
    party_id: uuid.UUID,
    websocket: WebSocket,
    token: Annotated[dict, Depends(decode_token)],
    websocket_chat_connection_service: Annotated[
        WebSocketChatConnectionService,
        Depends(get_websocket_chat_connection_service),
    ],
):
    await websocket_chat_connection_service.connect(
        token["username"], party_id, websocket
    )
