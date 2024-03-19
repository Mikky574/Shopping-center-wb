from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time  # 导入time模块处理时间戳
from database import TokenBlacklist  # 确保正确导入您的TokenBlacklist模型

DATABASE_URL = "sqlite:///./test.db"  # 或您实际使用的数据库URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def delete_expired_tokens():
    # 创建一个新的数据库会话
    db = SessionLocal()
    try:
        # 获取当前时间戳
        current_timestamp = int(time.time())
        # 查询并删除所有已经过期的token
        db.query(TokenBlacklist).filter(
            TokenBlacklist.expires_at < current_timestamp
        ).delete()
        db.commit()
        print("Expired tokens deleted successfully.")
    except Exception as e:
        print(f"Error while deleting expired tokens: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    delete_expired_tokens()
