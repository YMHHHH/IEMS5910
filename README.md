# 老年人语音呼救检测系统

面向老年人的语音呼救检测系统。当系统检测到"呼救"语音（如"help me"、"救命"等）时，端侧设备通过离线语音识别模块识别内容，若检测到为"呼救类"命令，则立即将事件发送到云端服务器。云端服务器再将该事件实时推送到前端Dashboard进行展示。

## 系统架构

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Python端侧设备  │────────▶│  Node.js后端服务器 │────────▶│  React前端      │
│  (Whisper识别)   │ WebSocket│  (MySQL存储)      │ WebSocket│  (实时Dashboard) │
└─────────────────┘         └──────────────────┘         └─────────────────┘
```

## 项目结构

```
demo/
├── device/              # Python端侧设备模拟器
│   ├── device.py       # 主程序
│   ├── whisper_handler.py  # Whisper识别模块
│   ├── config.py       # 配置管理
│   ├── audio_samples/  # 测试音频文件目录
│   └── requirements.txt
├── server/             # Node.js后端服务器
│   ├── server.js      # Express服务器
│   ├── database.js    # MySQL操作
│   └── package.json
├── dashboard/         # React前端Dashboard
│   ├── src/
│   └── package.json
└── database/          # 数据库相关
    └── schema.sql     # 数据库表结构
```

## 快速开始

### 1. 数据库设置

```bash
# 创建数据库和表
mysql -u root -p < database/schema.sql
```

### 2. 启动后端服务器

```bash
cd server
cp .env.example .env
# 编辑 .env 文件，设置数据库连接信息
npm install
npm start
```

服务器将在 `http://localhost:3001` 启动。

### 3. 启动前端Dashboard

```bash
cd dashboard
npm install
npm run dev
```

前端将在 `http://localhost:5173` 启动。

### 4. 运行端侧设备模拟器

```bash
cd device
pip install -r requirements.txt
# 将测试音频文件放入 audio_samples/ 目录
python device.py
```

## 环境配置

### Python端侧设备

通过环境变量配置：

```bash
export SERVER_URL=http://localhost:3001
export DEVICE_ID=elder-device-01
export WHISPER_MODEL=base
export MOCK_AUDIO=true
```

### Node.js后端

编辑 `server/.env` 文件：

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=elderly_voice_system
PORT=3001
```

## 技术栈

- **端侧**: Python 3.9+, Whisper (离线语音识别), Socket.io客户端
- **后端**: Node.js 18+, Express, Socket.io, MySQL
- **前端**: React 18+, Vite, Socket.io-client

## 功能特点

- ✅ **离线语音识别**: 使用Whisper在端侧进行识别，保护隐私
- ✅ **实时通信**: 基于WebSocket的实时事件推送
- ✅ **数据持久化**: MySQL数据库存储历史事件
- ✅ **实时监控**: React前端实时显示事件和设备状态

## 注意事项

1. **首次运行**: Whisper首次运行时会自动下载模型文件（base模型约150MB）
2. **音频文件**: 端侧设备需要测试音频文件，请将音频文件放入 `device/audio_samples/` 目录
3. **数据库**: 确保MySQL服务已启动，并正确配置连接信息
4. **端口冲突**: 确保3001（后端）和5173（前端）端口未被占用。如果5000端口被AirPlay占用，服务器会自动使用3001端口。


## 许可证

MIT
