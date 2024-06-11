from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Category
from utils import get_db
from typing import List
from pydantic import BaseModel

from typing import Optional

router = APIRouter()

# Pydantic模型用于响应格式化
class CategoryModel(BaseModel):
    id: int
    name: str
    children: Optional[List['CategoryModel']] = None

    class Config:
        orm_mode = True

# 构建树结构
def build_tree(node_id, adjacency_list, name_dict):
    node = {"id": node_id, "name": name_dict[node_id]}
    if node_id in adjacency_list:
        children = [build_tree(child_id, adjacency_list, name_dict) for child_id in adjacency_list[node_id]]
        if children:  # 仅当存在子节点时才添加children字段
            node["children"] = children
    return node

@router.get("/tree", response_model=List[CategoryModel])
async def get_category_tree(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    adjacency_list = {}
    name_dict = {}
    root_nodes = []

    for category in categories:
        name_dict[category.category_id] = category.name
        if category.parent_id == 0:
            root_nodes.append(category.category_id)

        if category.parent_id not in adjacency_list:
            adjacency_list[category.parent_id] = []
        adjacency_list[category.parent_id].append(category.category_id)

    tree_structure = [build_tree(root_id, adjacency_list, name_dict) for root_id in root_nodes]

    return tree_structure