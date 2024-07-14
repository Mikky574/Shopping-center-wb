from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Any
from pathlib import Path
working_dir = Path(__file__).parent
from fastapi import FastAPI
from apis import router as api_router

app = FastAPI(title='CQRobot-Online-Shop')
api = FastAPI(title=app.title, servers=[{'url': '/api'}])

# 商标
# 确保这个路径正确指向您的favicon.ico文件
ico_path = Path("catalog") / "opencart.ico"

@app.get("/favicon.ico", response_class=FileResponse)
async def get_logo_image():
    return ico_path


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
                    existing_cache_control = resp.headers.get('Cache-Control')
                    additional_cache_control = 'public, max-age=31536000, immutable'
                    # 如果原来的 Cache-Control 头部存在，则在其基础上追加
                    if existing_cache_control:
                        resp.headers['Cache-Control'] = existing_cache_control + ", " + additional_cache_control
                    else:
                        resp.headers['Cache-Control'] = additional_cache_control
            return resp

    app.mount(
        '/',
        CachedStaticFiles(directory=frontend_dist, html=True),
    )
    break
else:
    raise RuntimeError(f'Frontend dist directory {frontend_dist_dirs[0]} does not exist!')

# 包含auth路由
# api.include_router(auth_router)
api.include_router(api_router)

# 启动任务
from startup_tasks import run_tasks
@app.on_event("startup")
async def startup_event():
    # 执行定义在其他脚本的初始化任务
    run_tasks()