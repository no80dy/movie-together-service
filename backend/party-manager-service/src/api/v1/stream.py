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


@router.get("/{video_name}.m3u8")
async def stream_hls_video(
    video_name: str
):
    current_dir = Path(__file__).parents[3]
    video_path = current_dir.joinpath(f"hls/{video_name}/{video_name}.m3u8")
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


@router.get("/{segment_name}.ts")
async def stream_hls_segment(
    segment_name: str
):
    current_dir = Path(__file__).parents[3]
    ts_path = current_dir.joinpath(f"hls/video/{segment_name}.ts")
    return StreamingResponse(open(ts_path, "rb"), media_type="video/MP2T")
