## **用户相关API接口文档**

### **基础信息**

- **数据库**: SQLite, Redis
- **后台语言**: Python
- **框架**: FastAPI
- **密码哈希算法**: argon2i
- **API前缀**: `/api/users`

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
