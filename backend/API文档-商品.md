## **用户登录系统API接口文档**

### **基础信息**

- **数据库**: SQLite, Redis
- **后台语言**: Python
- **框架**: FastAPI
- **密码哈希算法**: argon2i
- **API前缀**: `/api`

### **获取商品**
#### **获取单个产品详细信息**

- **路径**: `/api/products/id/{product_id}`
- **方法**: `GET`
- **请求头**:
  - 无特殊请求头需求
- **路径参数**:
  - `product_id` (int, 必需): 欲查询的产品的唯一标识符。
- **成功响应体**:
  - `id` (int): 产品ID。
  - `model` (str): 产品模型。
  - `quantity` (int): 库存数量。
  - `image_url` (str): 产品图片的URL。
  - `price` (float): 产品价格。
  - `sold_count` (int, 可选): 销售数量。
  - `name` (str, 可选): 产品名称。
- **成功响应示例**:
  ```json
  {
    "id": 1099,
    "model": "CQRJSTEL-A",
    "quantity": 999,
    "image_url": "/api/image/catalog/CQRobot/JST EL/JST EL 2P-1.jpg",
    "price": 6.16,
    "sold_count": 500,
    "name": "JST EL - 2 Pin Connector Kit"
  }
  ```
- **失败响应**:
  - `404 Not Found`: `detail: "Product not found"` 如果提供的产品ID不存在。

### 获取产品描述
#### 获取单个产品描述信息

- **路径**: `/api/products/id/{product_id}/desc`
- **方法**: `GET`
- **请求头**:
  - 无特殊请求头需求
- **路径参数**:
  - `product_id` (int, 必需): 欲查询的产品的唯一标识符。
- **成功响应体**:
  - `description` (str): 产品描述（描述可能包含HTML内容）。
- **成功响应示例**:
  ```json
  {
    "description": "<p><font face="Tahoma"><span style="font-size: 12px;">Ocean: MCP23017 IO Expansion Board expands 2..."
  }
  ```
- **失败响应**:
  - `404 Not Found`: `detail: "Product description not found"` 如果提供的产品描述不存在。


#### **获取热门产品列表**

- **路径**: `/api/products/popular`
- **方法**: `GET`
- **请求头**:
  - 无特殊请求头需求
- **成功响应体**:
  - 列表形式返回，每个元素包含：
    - `id` (int): 产品ID。
    - `img_url` (str): 产品图片的URL。
    - `name` (str): 产品名称。
    - `model` (str): 产品模型。
- **成功响应示例**:
  ```json
  [
    {
      "id": 1120,
      "img_url": "catalog/CQRobot/MCP23017/MCP23017-1.JPG",
      "name": "Ocean: MCP23017 IO Expansion Board",
      "model": "CQRMCP23017A"
    },
    {
      "id": 993,
      "img_url": "catalog/CQRobot/2.0JST C/CQRJST2.0-C-1.jpg",
      "name": "JST PH - 2 / 3 / 4 Pin Connector Kit",
      "model": "CQRJSTPH-A"
    }
    // 更多产品...
  ]
  ```
- **失败响应**:
  - `404 Not Found`: `detail: "No popular products found"` 如果没有热门产品。
