from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Any
# 导入 database 包下的 auth 模块中的 router
from auth import router as auth_router

# 假设的 working_dir 定义，根据你的实际目录结构进行调整
from pathlib import Path
working_dir = Path(__file__).parent

app = FastAPI(title='CQRobot-Online-Shop')

api = FastAPI(title=app.title, servers=[{'url': '/api'}])
# api.openapi_version = '3.0.3'
app.mount(api.servers[0]['url'], api)

frontend_dist_dirs = (
    (working_dir / 'static'),
    (working_dir.parent / 'frontend' / 'dist'),
)

for frontend_dist in frontend_dist_dirs:
    if not frontend_dist.is_dir():
        continue

    class CachedStaticFiles(StaticFiles):
        def file_response(self, *args: Any, **kwargs: Any):
            resp = super().file_response(*args, **kwargs)
            if self.directory is not None and isinstance(resp, FileResponse):
                if (Path(self.directory) / 'assets') in Path(resp.path).parents:
                    if resp.headers.get('Cache-Control'):
                        print(resp.headers.get('Cache-Control'))
                    resp.headers['Cache-Control'] = (
                        'public, max-age=31536000, immutable, '
                        + resp.headers.get('Cache-Control', '')
                    )
            return resp

    app.mount(
        '/',
        CachedStaticFiles(directory=frontend_dist, html=True),
    )
    break
else:
    raise RuntimeError(f'Frontend dist directory {frontend_dist_dirs[0]} does not exist!')


# 包含auth路由
api.include_router(auth_router)

