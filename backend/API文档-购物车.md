## **用户登录系统API接口文档**

### **基础信息**

- **数据库**: SQLite, Redis
- **后台语言**: Python
- **框架**: FastAPI
- **密码哈希算法**: argon2i
- **API前缀**: `/api`

### 还未整理


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
