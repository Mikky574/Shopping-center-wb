from global_state import init_category_tree
from asyncio_tasks import start_tasks

def run_tasks():
    # 执行所有需要在启动时完成的任务
    init_category_tree()
    print("初始化完成。")
    start_tasks()
    print("所有定时任务已启动。")
