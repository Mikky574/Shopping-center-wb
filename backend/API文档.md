## **用户登录系统API接口文档**

### **基础信息**

- **数据库**: SQLite, Redis
- **后台语言**: Python
- **框架**: FastAPI
- **密码哈希算法**: argon2i
- **API前缀**: `/api`

### **接口列表**

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
  - `400 Bad Request`: 邮箱已被注册
  - `422 Unprocessable Entity`: 关键字段缺少

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
  - `400 Bad Request`: 邮箱或密码错误
  - `403 Forbidden`: 用户被禁用

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
  - `401 Unauthorized`: 令牌无效或未提供

#### **4. 用户登出**

- **路径**: `/api/users/logout`
- **方法**: `POST`
- **请求头**:
  - `Authorization`: 包含Bearer令牌
- **成功响应体**:
  - `message`: "You have been logged out."
- **失败响应**:
  - `401 Unauthorized`: 令牌无效或未提供

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
  - `401 Unauthorized`: 刷新令牌无效
  - `403 Forbidden`: 刷新令牌已过期或在黑名单中

#### *6. 重置密码**

- **路径**: `/api/users/reset_password`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "email": "user@example.com",
    "old_password": "currentpassword",
    "new_password": "newpassword123"
  }
  ```
  - `email` (EmailStr): 用户的邮箱地址，用于标识用户账户。
  - `old_password` (str): 用户当前的密码。
  - `new_password` (str): 用户希望设置的新密码。

- **成功响应体**:
  ```json
  {
    "message": "Password has been reset successfully."
  }
  ```
  表示密码已成功重置。

- **失败响应**:
  - `404 Not Found`: 未找到用户，邮箱可能未注册。
  - `400 Bad Request`: 旧密码不正确或请求体格式错误。


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



<!-- 
# 用户登录系统API接口文档

## 基础信息

- **数据库**: SQLite, Redis
- **后台语言**: Python
- **框架**: FastAPI
- **密码哈希算法**: argon2i
- **API前缀**: `/api`

## 接口列表

### 1. 用户注册

- **路径**: `/api/users/register`
- **方法**: `POST`
- **状态码**: `200 OK`
- **请求体**:
  - `email` (EmailStr): 用户邮箱（必须，需符合邮箱格式）
  - `password` (str): 用户密码（必须）
  - `first_name` (str, 可选): 用户名
  - `last_name` (str, 可选): 用户姓
  - `phone_number` (str, 可选): 用户电话号码
- **成功响应体**:
  ```json
  {
    "message": "User registered successfully."
  }
  ```
- **失败响应**:
  - `400 Bad Request`: 邮箱已被注册

### 2. 用户登录

- **路径**: `/api/users/login`
- **方法**: `POST`
- **请求体**:
  - `email` (str): 用户邮箱
  - `password` (str): 用户密码
- **成功响应体**:
  ```json
  {
    "access_token": "<token>",
    "token_type": "bearer",
    "expires_in": 1440
  }
  ```
- **失败响应**:
  - `400 Bad Request`: 邮箱或密码错误
  - `403 Forbidden`: 用户被禁用

### 3. 获取当前用户信息

- **路径**: `/api/me`
- **方法**: `GET`
- **头部**: 需要携带`Authorization`字段，值为`Bearer <access_token>`
- **成功响应体**:
  ```json
  {
    "email": "<EmailStr>",
    "first_name": "<str>",
    "last_name": "<str>",
    "phone_number": "<str>"
  }
  ```
- **失败响应**:
  - `404 Not Found`: 用户信息未找到 -->


### 重置密码

- **路径**: `/api/users/reset-password`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "email": "user@example.com",
    "old_password": "currentpassword",
    "new_password": "newpassword123"
  }
  ```
  - `email` (EmailStr): 用户的邮箱地址，用于标识用户账户。
  - `old_password` (str): 用户当前的密码。
  - `new_password` (str): 用户希望设置的新密码。

- **成功响应体**:
  ```json
  {
    "message": "Password has been reset successfully."
  }
  ```
  表示密码已成功重置。

- **失败响应**:
  - `404 Not Found`: 未找到用户，邮箱可能未注册。
  - `400 Bad Request`: 旧密码不正确或请求体格式错误。

### 注意事项

- 后端我没限定旧密码一定得要和新密码不同，这个在前端来保证就行了