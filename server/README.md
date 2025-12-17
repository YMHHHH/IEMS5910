# 后端服务器


Node.js + Express + Socket.io + MySQL 后端服务器。

### 功能特点

- ✅ WebSocket 服务器（Socket.io）
- ✅ REST API 接口
- ✅ MySQL 数据库存储
- ✅ 实时事件广播

### 环境要求

- Node.js 18+
- MySQL 5.7+ 或 MySQL 8.0+

### 数据库设置

1. 使用提供的 SQL 脚本创建数据库：
```bash
mysql -u root -p < ../database/schema.sql
```

2. 或手动创建并执行脚本中的表结构：
```sql
CREATE DATABASE elderly_voice_system;
USE elderly_voice_system;
-- 然后执行 database/schema.sql 中的表创建语句
```

### 安装依赖

```bash
cd server
npm install
```

### 配置

1. 复制环境变量示例文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，设置数据库连接信息：
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=elderly_voice_system
PORT=5000
```

（注意：运行时显示的端口可能与 `.env` 中的 `PORT` 不同，具体以项目启动日志为准。）

### 运行

```bash
npm start
```

服务器将在 `http://localhost:3001` 启动（请以终端启动信息为准）。

### API 接口

#### GET /api/events
获取历史事件列表。

查询参数：
- `limit`: 返回数量限制（默认 100）
- `offset`: 偏移量（默认 0）

示例：
```
GET /api/events?limit=50&offset=0
```

#### GET /api/stats
获取统计信息。

返回示例：
```json
{
  "connectedClients": 2
}
```

### Socket.io 事件

接收事件：
- `voice-event`：接收来自 Python 客户端或设备端的语音事件。

发送事件：
- `new-event`：向所有前端客户端广播新事件。
- `client-count-update`：客户端连接数更新。

---

Node.js + Express + Socket.io + MySQL backend server.

### Features

- ✅ WebSocket server (Socket.io)
- ✅ REST API endpoints
- ✅ MySQL database storage
- ✅ Real-time event broadcasting

### Requirements

- Node.js 18+
- MySQL 5.7+ or MySQL 8.0+

### Database setup

1. Create the database using the provided script:
```bash
mysql -u root -p < ../database/schema.sql
```

2. Or create it manually and then run the table creation statements from `database/schema.sql`:
```sql
CREATE DATABASE elderly_voice_system;
USE elderly_voice_system;
-- then run the table creation statements from database/schema.sql
```

### Install dependencies

```bash
cd server
npm install
```

### Configuration

1. Copy the example env file:
```bash
cp .env.example .env
```

2. Edit `.env` and set database connection information:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=elderly_voice_system
PORT=5000
```

Note: The actual listening port may be shown differently in the startup logs; use the logs to confirm.

### Run

```bash
npm start
```

The server will start on `http://localhost:3001` (check the startup logs).

### API Endpoints

#### GET /api/events
Retrieve historical events.

Query params:
- `limit`: maximum number of results (default 100)
- `offset`: offset (default 0)

Example:
```
GET /api/events?limit=50&offset=0
```

#### GET /api/stats
Get statistics.

Response example:
```json
{
  "connectedClients": 2
}
```

### Socket.io Events

Incoming events:
- `voice-event`: events received from Python clients or devices.

Outgoing events:
- `new-event`: broadcast new events to all frontend clients.
- `client-count-update`: update connected clients count.
