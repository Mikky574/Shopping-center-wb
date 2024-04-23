# from fastapi import APIRouter, HTTPException, Header
# from fastapi.responses import FileResponse, Response
# from pathlib import Path
# import os
# from datetime import datetime, timezone

# router = APIRouter()

# base_dir = Path(__file__).resolve().parent.parent
# catalog_dir = base_dir / "catalog"

# @router.get("/cache/catalog/{file_path:path}")
# async def fetch_image(file_path: str, if_modified_since: datetime = Header(None)):
#     file_location = catalog_dir / file_path
#     if not file_location.exists() or not file_location.is_file():
#         raise HTTPException(status_code=404, detail="File not found")

#     # 获取文件的最后修改时间
#     file_stat = os.stat(file_location)
#     last_modified = datetime.fromtimestamp(file_stat.st_mtime, timezone.utc)

#     # 比较 'If-Modified-Since' 头与文件的最后修改时间
#     if if_modified_since is not None and last_modified <= if_modified_since.replace(tzinfo=timezone.utc):
#         return Response(status_code=304)

#     headers = {
#         "Cache-Control": "public, max-age=600",
#         "Last-Modified": last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT"),
#         # 添加 ETag 或其他相关头部
#     }

#     return FileResponse(path=file_location, media_type='image/jpeg', headers=headers)


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

@router.get("/cache/catalog/{file_path:path}")
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
            raise HTTPException(status_code=400, detail="Invalid 'If-Modified-Since' header format")

    headers = {
        "Cache-Control": "public, max-age=600",
        "Last-Modified": last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")
    }

    return FileResponse(path=file_location, media_type='image/jpeg', headers=headers)
