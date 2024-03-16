from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
# 导入 database 包下的 auth 模块中的 router
from auth import router as auth_router

app = FastAPI()

# 挂载静态文件目录
app.mount("/assets", StaticFiles(directory="dist/assets", html=True), name="assets")

@app.get("/")
async def root():
    return FileResponse('dist/index.html')

# 包含auth路由
app.include_router(auth_router)
