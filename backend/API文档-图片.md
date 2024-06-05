## **用户登录系统API接口文档**

### **基础信息**

- **数据库**: SQLite, Redis
- **后台语言**: Python
- **框架**: FastAPI
- **密码哈希算法**: argon2i
- **API前缀**: `/api`

### **获取图像文件接口**
- **路径**: `/api/image/{file_path:path(/catalog开头的图片路径)}`
- **方法**: `GET`
- **请求体**:
  - `file_path` (路径参数，必须): 图像文件的路径，会检查，只响应catalog开头的。
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

### **获取Logo图片路径接口**

- **路径**: `/api/logo`
- **方法**: `GET`
- **请求体**: 无
- **成功响应**:
  - **状态码**: `200 OK`
  - **响应体**: `/api/image/catalog/xxxx.png`

- **备注**: 该接口返回前端可用于获取Logo图片的完整API路径，不直接返回图像文件，而是返回构造的路径信息。

### **获取Carousel图片路径列表接口**

- **路径**: `/api/carousel`
- **方法**: `GET`
- **请求体**: 无
- **成功响应**:
  - **状态码**: `200 OK`
  - **响应体**: [`/api/image/catalog/aaaa.png`,`/api/image/catalog/bbbb.png`,......] 包含Carousel中所有图片的API路径列表。

