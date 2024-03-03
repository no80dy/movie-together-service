import os
import uuid
from pathlib import Path
from typing import Annotated

from api.v1.auth import security_jwt
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
    if not party:
        return templates.TemplateResponse(
            "forbidden.html", {"request": request}
        )
    return templates.TemplateResponse(
        "stream.html",
        {
            "request": request,
            "stream_link": f"http://localhost:8000/api/v1/stream/hls/video/video.m3u8",
            "websocket_stream_link": f"ws://localhost:8000/ws/stream/{party_id}?token={token}",
            "websocket_chat_link": f"ws://localhost:8000/ws/chat/{party_id}?token={token}",
        },
    )


@router.get("/hls/{folder_name}/{video_name}.m3u8")
async def stream_hls_video(folder_name: str, video_name: str):
    current_dir = Path(__file__).parents[3]
    video_path = current_dir.joinpath(f"hls/{folder_name}/{video_name}.m3u8")
    if os.path.exists(video_path):

        def generate():
            with open(video_path, "rb") as video_file:
                while True:
                    chunk = video_file.read(1024)
                    if not chunk:
                        break
                    yield chunk

        return StreamingResponse(
            generate(), media_type="application/vnd.apple.mpegurl"
        )
    else:
        return Response(content="Video file not found", status_code=404)


@router.get("/hls/{folder_name}/{segment_name}.ts")
async def stream_hls_segment(folder_name: str, segment_name: str):
    current_dir = Path(__file__).parents[3]
    ts_path = current_dir.joinpath(f"hls/{folder_name}/{segment_name}.ts")
    return StreamingResponse(open(ts_path, "rb"), media_type="video/MP2T")
