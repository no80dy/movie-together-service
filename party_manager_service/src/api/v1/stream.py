import os
import uuid
from pathlib import Path
from typing import Annotated

from api.v1.auth import security_jwt
from core.config import settings
from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response, StreamingResponse
from fastapi.templating import Jinja2Templates
from services.broker import PartyManagerService, get_party_manager_service

router = APIRouter()

templates_dir = Path(__file__).parents[2].joinpath("templates")
templates = Jinja2Templates(directory=templates_dir)


@router.get("/{party_id}")
async def stream_film(
    request: Request,
    party_id: uuid.UUID,
    token: Annotated[str, Depends(security_jwt)],
    party_manager_service: Annotated[
        PartyManagerService, Depends(get_party_manager_service)
    ],
):
    party = await party_manager_service.find_party_by_id(party_id=party_id)
    film_id = party["film_id"]
    if not party:
        return templates.TemplateResponse(
            "forbidden.html", {"request": request}
        )
    return templates.TemplateResponse(
        "stream.html",
        {
            "request": request,
            "stream_link": f"{settings.media_service_url}/{film_id}/{film_id}.m3u8",
            "websocket_stream_link": f"/stream/{party_id}?token={token}",
            "websocket_chat_link": f"/chat/{party_id}?token={token}",
        },
    )
