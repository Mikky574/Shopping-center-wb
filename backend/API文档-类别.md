## 待解决，还没和商品挂钩，在源数据表中，商品是有个类别id的

#### **所有类别查询**

- **路径**: `/api/categories/tree`
- **方法**: `GET`
- **状态码**: `200 OK`
- **请求体**: 无
- **成功响应体**:
  - **描述**: 返回所有类别的树形结构。
  - **示例**:
    ```json
    [
        {
            "id": 1,
            "name": "Root 1",
            "children": [
                {
                    "id": 2,
                    "name": "Child 1-1",
                    "children": []
                },
                {
                    "id": 3,
                    "name": "Child 1-2",
                    "children": []
                }
            ]
        },
        {
            "id": 4,
            "name": "Root 2",
            "children": [
                {
                    "id": 5,
                    "name": "Child 2-1",
                    "children": []
                }
            ]
        }
    ]
    ```
- **失败响应**:
  - **描述**: 空list
  - **示例**:
    ```json
    []
    ```
