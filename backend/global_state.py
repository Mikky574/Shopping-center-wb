from typing import Any, Dict, List
from sqlalchemy.orm import Session
from database import Category, CategoryDescription
from utils import get_db

# apis/categories.py的相关任务
category_tree: List[Dict[str, Any]] = []

def build_tree(node_id, adjacency_list, name_dict):
    node = {"id": node_id, "name": name_dict[node_id]}
    if node_id in adjacency_list:
        children = [build_tree(child_id, adjacency_list, name_dict) for child_id in adjacency_list[node_id]]
        if children:
            node["children"] = children
    return node

def update_category_tree(new_tree: List[Dict[str, Any]]):
    global category_tree
    category_tree = new_tree

def get_category_tree() -> List[Dict[str, Any]]:
    return category_tree

def init_category_tree():
    db: Session = next(get_db())  # 获取数据库会话
    try:
        categories = db.query(Category).all()  # 查询所有分类
        descriptions = db.query(CategoryDescription).all()  # 查询所有分类描述

        name_dict = {desc.category_id: desc.name for desc in descriptions}  # 构建ID到名称的映射
        adjacency_list = {}  # 初始化邻接列表
        root_nodes = []  # 初始化根节点列表

        for category in categories:
            if category.parent_id == 0:
                root_nodes.append(category.category_id)  # 收集根节点

            if category.parent_id not in adjacency_list:
                adjacency_list[category.parent_id] = []
            adjacency_list[category.parent_id].append(category.category_id)  # 填充邻接列表

        # 使用构建的数据构造树结构
        tree_structure = [build_tree(root_id, adjacency_list, name_dict) for root_id in root_nodes]
        update_category_tree(tree_structure)  # 更新全局变量
    finally:
        db.close()  # 确保数据库会话被关闭
