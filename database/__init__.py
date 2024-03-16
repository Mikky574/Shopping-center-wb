from .models import Base, User  # 导入Base和所有的模型类
from .database import SessionLocal, engine  # 导入数据库会话和引擎

# 导入此包时，确保所有模型都已导入，以便Base类可以
# 在需要时创建所有表
Base.metadata.create_all(bind=engine)
