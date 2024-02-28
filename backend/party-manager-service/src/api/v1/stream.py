import uuid
import jinja2
import os
from io import BytesIO
from typing import Annotated
from pathlib import Path

from fastapi import APIRouter, Query, Header
from fastapi.responses import (
	StreamingResponse, HTMLResponse, FileResponse, Response
)


router = APIRouter()


@router.get("/video.m3u8")
async def stream_hls_video():
    video_path = "/home/aleksandr/Development/repo/movie-together-service/backend/party-manager-service/src/hls/video.m3u8"
    if os.path.exists(video_path):
        def generate():
            with open(video_path, "rb") as video_file:
                while True:
                    chunk = video_file.read(1024)
                    if not chunk:
                        break
                    yield chunk

        return StreamingResponse(generate(), media_type="application/vnd.apple.mpegurl")
    else:
        return Response(content="Video file not found", status_code=404)


@router.get("/{segment}")
async def stream_hls_segment(
    segment: str
):
    ts_dir = "/home/aleksandr/Development/repo/movie-together-service/backend/party-manager-service/src/hls/"
    ts_file_path = ts_dir + segment
    return StreamingResponse(open(ts_file_path, "rb"), media_type="video/MP2T")
