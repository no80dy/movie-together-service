from pathlib import Path as FilePath
from typing import Annotated

from fastapi import APIRouter, Path
from fastapi.responses import Response, StreamingResponse

CHUNK_SIZE = 1024

router = APIRouter()
current_dir = FilePath(__file__).parents[2]


def generate(m3u8_file_path: FilePath):
    with open(m3u8_file_path, "rb") as video_file:
        while True:
            chunk = video_file.read(CHUNK_SIZE)
            if not chunk:
                break
            yield chunk


@router.get(
    "/{folder_name}/{video_name}.m3u8",
    summary="Трансляция файла .m3u8",
    description="Транслирует основной файл видео, который указывает на сегменты",
)
async def stream_hls_video(
    folder_name: Annotated[str, Path(description="Название папки фильма")],
    video_name: Annotated[
        str, Path(description="Название .m3u8 файла фильма")
    ],
):
    m3u8_file_path = current_dir.joinpath(
        f"hls/{folder_name}/{video_name}.m3u8"
    )
    if m3u8_file_path.exists():
        return StreamingResponse(
            generate(m3u8_file_path),
            media_type="application/vnd.apple.mpegurl",
        )
    else:
        return Response(content="Video file not found", status_code=404)


@router.get(
    "/{folder_name}/{segment_name}.ts",
    summary="Трансляция файла .ts",
    description="Транслирует сегменты фидеопотока видео",
)
async def stream_hls_segment(
    folder_name: Annotated[str, Path(description="Название папки фильма")],
    segment_name: Annotated[
        str, Path(description="Название .ts файлов фильма")
    ],
):
    ts_file_path = current_dir.joinpath(f"hls/{folder_name}/{segment_name}.ts")
    return StreamingResponse(open(ts_file_path, "rb"), media_type="video/MP2T")
