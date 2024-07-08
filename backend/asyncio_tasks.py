# 定时任务的代码模板
# another_task_lock = Lock()
# async def periodic_another_task():
#     while True:
#         await asyncio.sleep(30)  # 假设另一个任务每30秒执行一次
#         with another_task_lock:
#             another_update_task()
#             print("另一个任务已更新")

import asyncio
from asyncio import Lock
from global_state import init_category_tree
import time
from database import AccTokenMapping
from utils import get_db

# 定义任务锁，使用 asyncio 的 Lock
update_tree_lock = Lock()

async def periodic_update_tree_task():
    while True:
        await asyncio.sleep(60*3)  # 每3分钟更新一次分类树
        async with update_tree_lock:
            init_category_tree()
            print("分类树已更新")

async def periodic_token_cleanup_task():
    while True:
        await asyncio.sleep(60*60*24*7)  # 一周执行一次
        await delete_expired_tokens_async()

async def delete_expired_tokens_async():
    db = next(get_db())  # 使用 get_db 生成器获取数据库会话
    try:
        current_timestamp = int(time.time())
        db.query(AccTokenMapping).filter(
            AccTokenMapping.exp_at < current_timestamp
        ).delete()
        db.commit()
        print("过期的令牌已被清理")
    except Exception as e:
        print(f"遇到错误，错误tokens: {e}")
    finally:
        db.close()

def start_tasks():
    # 创建并返回所有任务的列表
    return [
        asyncio.create_task(periodic_update_tree_task()),
        asyncio.create_task(periodic_token_cleanup_task()),
        # asyncio.create_task(periodic_another_task())
    ]
