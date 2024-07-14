from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import FileResponse
from starlette.responses import Response
from pathlib import Path
import os
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

router = APIRouter()

base_dir = Path(__file__).resolve().parent.parent
catalog_dir = base_dir / "catalog"

@router.get("/catalog/{file_path:path}")
async def fetch_image(file_path: str, if_modified_since: str = Header(None)):
    file_location = catalog_dir / file_path
    if not file_location.exists() or not file_location.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    file_stat = os.stat(file_location)
    last_modified = datetime.fromtimestamp(file_stat.st_mtime, timezone.utc)

    if if_modified_since:
        try:
            if_modified_since = parsedate_to_datetime(if_modified_since)
            if last_modified <= if_modified_since:
                return Response(status_code=304)
        except Exception:
            raise HTTPException(
                status_code=400, detail="Invalid 'If-Modified-Since' header format"
            )

    headers = {
        "Cache-Control": "public, max-age=600",
        "Last-Modified": last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT"),
    }

    return FileResponse(path=file_location, media_type="image/jpeg", headers=headers)


def construct_api_path(file_path: str) -> str:
    return f"/api/image/{file_path}"

# 先创建路径对象
logo_path = Path("catalog") / "opencart-logo.png"

carousel_paths = [
    Path("catalog") / "AngelDT-9000DEA.JPG",
    Path("catalog") / "JST-EL2Pin.jpg",
    Path("catalog") / "journal3" / "gallery" / "mikey-wu-1187454-unsplash.jpg",
    Path("catalog") / "journal3" / "banners" / "behar-zenuni-797461-unsplash.jpg",
    Path("catalog") / "1.JPG",
    Path("catalog") / "journal3" / "banners" / "jess-watters-500955-unsplash.jpg",
]
ico_path= Path("catalog") / "opencart.ico"
@router.get("/favicon.ico", response_model=str)
async def get_logo_image():
    return construct_api_path(str(ico_path))

@router.get("/logo", response_model=str)
async def get_logo_image():
    return construct_api_path(str(logo_path))

@router.get("/carousel", response_model=list)
async def get_images():
    paths_list = [construct_api_path(str(path)) for path in carousel_paths]
    if not paths_list:
        raise HTTPException(status_code=404, detail="Images not found")
    return paths_list

