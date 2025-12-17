# 前端Dashboard

React + Vite + Socket.io-client 实时监控面板。

## 功能特点

- ✅ 实时显示语音事件
- ✅ 区分紧急和非紧急事件
- ✅ 显示活跃设备数
- ✅ 自动重连机制

## 环境要求

- Node.js 18+
- npm 或 yarn

## 安装依赖

```bash
cd dashboard
npm install
```

## 运行开发服务器

### 本地开发（默认）

```bash
npm run dev
```

前端将在 `http://localhost:5173` 启动，默认连接到 `http://localhost:3001`。

### 使用 ngrok 或其他远程服务器

1. 创建 `.env` 文件（在 `dashboard` 目录下）：
```bash
# .env
VITE_SERVER_URL=https://xxxx-xx-xx-xx-xx.ngrok-free.app
```
```markdown
# 前端 Dashboard / Frontend Dashboard

本仓库包含一个基于 React + Vite + Socket.io-client 的实时监控面板，用于展示来自设备端的语音事件。

---

## 中文说明

### 功能特点

- ✅ 实时显示语音事件
- ✅ 区分紧急和非紧急事件
- ✅ 显示活跃设备数（在线设备计数）
- ✅ 自动重连机制（Socket.IO）

### 环境要求

- Node.js 18+
- npm 或 yarn

### 安装依赖

```bash
cd dashboard
npm install
```

### 运行开发服务器

#### 本地开发（默认）

```bash
npm run dev
```

前端将在 `http://localhost:5173` 启动，默认连接到 `http://localhost:3001`（后端地址）。

#### 使用 ngrok 或其他远程服务器

1. 在 `dashboard` 目录下创建或编辑 `.env`：
```env
# .env
VITE_SERVER_URL=https://your-ngrok-or-domain.example
```

2. 或临时通过环境变量运行（无需修改文件）：
```bash
VITE_SERVER_URL=https://your-ngrok-or-domain.example npm run dev
```

3. 启动开发服务器：
```bash
npm run dev
```

注意：
- 使用 ngrok 时请填写完整的 URL（包含 `https://`），以便 Socket.IO 使用 WSS。
- 未设置 `VITE_SERVER_URL` 时，前端会回退到 `http://localhost:3001`。
- 修改 `.env` 后需要重启开发服务器以生效。

### 构建生产版本

```bash
npm run build
```

### 项目结构

```
dashboard/
├── src/
│   ├── App.jsx           # 主应用组件
│   ├── main.jsx          # 入口文件
│   ├── components/       # 组件
│   │   ├── EventList.jsx
│   │   ├── EventCard.jsx
│   │   └── StatusBar.jsx
│   ├── hooks/            # 自定义 Hook
│   │   └── useSocket.js
│   └── index.css         # 全局样式
├── index.html            # HTML 模板
└── vite.config.js        # Vite 配置
```

---

## English Instructions

This dashboard is a real-time monitoring UI built with React, Vite and Socket.IO-client. It visualizes voice events emitted by the device clients.

### Features

- ✅ Real-time voice events
- ✅ Distinguish emergency / non-emergency events
- ✅ Shows number of active devices
- ✅ Auto-reconnect with Socket.IO

### Requirements

- Node.js 18+
- npm or yarn

### Install dependencies

```bash
cd dashboard
npm install
```

### Run development server

#### Local (default)

```bash
npm run dev
```

The frontend will start at `http://localhost:5173` and, by default, connect to the backend at `http://localhost:3001`.

#### Using ngrok or a remote backend

1. Create an `.env` file in the `dashboard` directory:
```env
# .env
VITE_SERVER_URL=https://your-ngrok-or-domain.example
```

2. Or run with a temporary environment variable:
```bash
VITE_SERVER_URL=https://your-ngrok-or-domain.example npm run dev
```

3. Start the dev server:
```bash
npm run dev
```

Notes:
- When using ngrok, make sure to use the full https URL so Socket.IO can use WSS.
- If `VITE_SERVER_URL` is not set, the app falls back to `http://localhost:3001`.
- Restart the dev server after changing `.env`.

### Build for production

```bash
npm run build
```

### Project structure

```
dashboard/
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   ├── components/
│   ├── hooks/
│   └── index.css
├── index.html
└── vite.config.js
```

``` 
