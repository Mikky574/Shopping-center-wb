## **用户登录系统API接口文档**

### **基础信息**

- **数据库**: SQLite, Redis
- **后台语言**: Python
- **框架**: FastAPI
- **密码哈希算法**: argon2i
- **API前缀**: `/api`

### **用户系列接口列表**

##### 注意，JWT中我删除了前端保存刷新令牌的逻辑，现在刷新令牌在后台，前端只需要附带通行令牌信息访问即可。可能返回结果是通行令牌过期，这时候需要访问 刷新令牌 然后再重新负载新的通行令牌再请求一次。

#### **1. 用户注册**

- **路径**: `/api/users/register`
- **方法**: `POST`
- **状态码**: `200 OK`
- **请求体**:
  - `email` (EmailStr): 用户邮箱（必须，需符合邮箱格式）
  - `password` (str): 用户密码（必须）
  - `first_name` (str, 必须): 用户名
  - `last_name` (str, 必须): 用户姓
  - `phone_number` (str, 必须): 用户电话号码
- **成功响应体**:
  - `message`: "User registered successfully."
- **失败响应**:
  - `400 Bad Request`: `detail:{"Email already registered"}` 邮箱已被注册
  - `422 Unprocessable Entity`: `detail:{"At least one of the following must be provided: first_name, last_name, phone_number"}` 关键字段缺少

#### **2. 用户登录**

- **路径**: `/api/users/login`
- **方法**: `POST`
- **请求体**:
  - `email` (str): 用户邮箱
  - `password` (str): 用户密码
- **成功响应体**:
  - `access_token` (str): 授权令牌
  - `token_type` (str): 令牌类型，固定值"bearer"
  - `expires_in` (int): 令牌过期时间，默认acc为3h，单位为分钟
- **失败响应**:
  - `400 Bad Request`: `detail:{"Incorrect email or password"}` 邮箱或密码错误
  - `403 Forbidden`: `detail:{"User is disabled"}` 用户被禁用 (注释：只是留了个信息在这里，目前不会触发禁用)

#### **3. 获取当前用户信息**

- **路径**: `/api/users/me`
- **方法**: `GET`
- **请求头**:
  - `Authorization`: 需包含有效的Bearer令牌
- **成功响应体**:
  - `email` (EmailStr): 用户邮箱
  - `first_name` (str, 可选): 用户名
  - `last_name` (str, 可选): 用户姓
  - `phone_number` (str, 可选): 用户电话号码
- **失败响应**:
  - `401 Unauthorized`: `detail:{"Token has expired"}` 令牌过期
  - `401 Unauthorized`: `detail:{"Token is invalid"}` 令牌无效
  - `401 Unauthorized`: `detail:{"User not found"}` 未找到用户，邮箱可能未注册。
  - `404 Not Found`: `detail:{"User information not found"}` 未找到用户信息。 (注释：暂时没有触发条件，目前不会被触发)

#### **4. 用户登出**

- **路径**: `/api/users/logout`
- **方法**: `POST`
- **请求头**:
  - `Authorization`: 包含Bearer令牌
- **成功响应体**:
  - `message`: "You have been logged out."
- **失败响应**:
  - `401 Unauthorized`: `detail:{"Token has expired"}` 令牌过期
  - `401 Unauthorized`: `detail:{"Token is invalid"}` 令牌无效
  - `404 Not Found`: `detail:{"Token record not found"}` 重复登出会报的错误

#### **5. 刷新访问令牌**

- **路径**: `/api/users/refresh_token`
- **方法**: `POST`
- **请求头**:
  - `Authorization`: 包含旧的Bearer令牌
- **成功响应体**:
  - `access_token` (str): 新的授权令牌
  - `token_type` (str): 令牌类型，固定值"bearer"
  - `expires_in` (int): 授权令牌有效期（秒），令牌过期时间，默认acc为3h，单位为分钟
- **失败响应**:
  - `401 Unauthorized`: `detail:{"Token is invalid"}` 通行令牌无效，假的令牌
  - `403 Forbidden`: `detail:{"Refresh token is invalid or expired"}` 刷新令牌已过期或无效，需要重新登录

#### **6. 重置密码**

- **路径**: `/api/users/reset_password`
- **方法**: `POST`
- **请求体**:
  - `email` (EmailStr): 用户的邮箱地址，用于标识用户账户。
  - `old_password` (str): 用户当前的密码。
  - `new_password` (str): 用户希望设置的新密码。

- **成功响应体**:
  - `message`: "Password has been reset successfully." 表示密码已成功重置。

- **失败响应**:
  - `404 Not Found`: `detail:{"User not found"}` 未找到用户，邮箱可能未注册。
  - `400 Bad Request`: `detail:{"Incorrect password"}` 旧密码不正确或请求体格式错误。
- 后端我没限定旧密码一定得要和新密码不同



### **获取图像文件接口**
- **路径**: `/cache/catalog/{file_path:path}`
- **方法**: `GET`
- **请求体**:
  - `file_path` (路径参数，必须): 图像文件相对路径。
  - `if_modified_since` (请求头，可选): 用于条件请求的时间戳，表示如果文件自指定时间以来未被修改，则返回304 Not Modified。

- **成功响应**: `200 OK`
- **响应体**: 图像文件内容。
- **响应头**:
  - `Cache-Control`: 指定缓存策略，`public, max-age=600` 表示该文件可以被公共缓存，并且缓存有效期为600秒。
  - `Last-Modified`: 文件的最后修改时间，用于条件请求。

- **失败响应**:
  - **状态码**: `404 Not Found`
  - **状态码**: `400 Bad Request` 无效的 `If-Modified-Since` 头的错误详情，表示客户端提供的条件请求时间格式错误。

- **备注**: 该接口允许客户端通过指定文件路径获取图像文件，并提供了缓存控制和条件请求功能。



### **获取商品**
#### **获取单个产品详细信息**

- **路径**: `/api/products/product/{product_id}`
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
  - `name` (str): 产品名称。
  - `description` (str): 产品描述（描述可能包含HTML内容）。
- **成功响应示例**:
  ```json
  {
    "id": 1099,
    "model": "CQRJSTEL-A",
    "quantity": 999,
    "image_url": "catalog/CQRobot/JST EL/JST EL 2P-1.jpg",
    "price": 6.16,
    "name": "JST EL - 2 Pin Connector Kit",
    "description": "Detailed description here..."
  }
  ```
- **失败响应**:
  - `404 Not Found`: `detail: "Product not found"` 如果提供的产品ID不存在。

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



<!-- 数据库还在改 -->


| 模型     | 字段              | 类型         | 描述                                   | 关系                                 |
|----------|-------------------|--------------|--------------------------------------|--------------------------------------|
| **User** | id                | Integer      | 主键，自增长，唯一标识用户             |                                      |
|          | email             | String       | 必须唯一，用于用户登录                 |                                      |
|          | hashed_password   | String       | 存储加密后的用户密码                   |                                      |
|          | disabled          | Boolean      | 默认为`False`，表示用户是否被禁用     |                                      |
|          | info              | relationship | 表示与`UserInfo`模型的一对一关系       | 通过`UserInfo`的`user_id`与之关联     |
| **UserInfo** | id            | Integer      | 主键，自增长，唯一标识用户信息         |                                      |
|          | user_id           | Integer      | 外键，指向`users.id`，唯一             |                                      |
|          | first_name        | String       | 存储用户的名                           |                                      |
|          | last_name         | String       | 存储用户的姓                           |                                      |
|          | phone_number      | String       | 存储用户的电话号码                     |                                      |
|          | user              | relationship | 表示与`User`模型的反向一对一关系       | 通过`User`的`info`与之相连            |


uvicorn main:app --reload
