数据库：SQLite
后台语言：Python
后台建站框架：fastapi
    用户登录系统：
密码哈希函数：argon2i
API：/users
用户注册:
- **Endpoint**: `POST /users/register`
- **Body**:
  ```json
  {
    "username": "user1",
    "password": "password123"
  }
  ```
用户登录:
- **Endpoint**: `POST /users/login`
- **Body**:
  ```json
  {
    "username": "user1",
    "password": "password123"
  }
  ```

