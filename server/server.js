/**
 * 老年人语音呼救检测系统 - 后端服务器
 * Express + Socket.io + MySQL
 */

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const { initDatabase, saveEvent, getEvents, closeDatabase } = require('./database');

const app = express();
const server = http.createServer(app);

// 配置CORS
const io = new Server(server, {
    transports:['websocket'],
    cors: {
        origin: '*',
        methods: ['GET', 'POST']
    }
});

app.use(cors());
app.use(express.json());

// 存储连接的客户端
const connectedClients = new Set();

// REST API路由

/**
 * 获取历史事件列表
 * GET /api/events?limit=100&offset=0
 */
app.get('/api/events', async (req, res) => {
    try {
        const limit = parseInt(req.query.limit) || 100;
        const offset = parseInt(req.query.offset) || 0;
        
        const events = await getEvents(limit, offset);
        res.json(events);
    } catch (error) {
        console.error('获取事件列表失败:', error);
        res.status(500).json({ error: '获取事件列表失败' });
    }
});

/**
 * 获取统计信息
 * GET /api/stats
 */
app.get('/api/stats', (req, res) => {
    res.json({
        connectedClients: connectedClients.size
    });
});

// Socket.io连接处理
io.on('connection', (socket) => {
    console.log(`✅ 客户端已连接: ${socket.id}`);
    connectedClients.add(socket.id);
    
    // 通知所有客户端连接数更新
    io.emit('client-count-update', connectedClients.size);
    
    // 接收来自设备的事件
    socket.on('voice-event', async (data) => {
        try {
            // 验证事件格式
            if (!data.device_id || typeof data.is_emergency !== 'boolean') {
                console.warn('⚠️  事件格式无效:', data);
                socket.emit('error', { message: '事件格式无效' });
                return;
            }
            
            // 如果text为空，跳过处理但不上报错误（可能是静音或识别失败）
            if (!data.text || data.text.trim() === '') {
                console.log('⚠️  收到空文本事件，跳过保存:', data.device_id);
                return;
            }
            
            console.log('📢 收到语音事件:', {
                device_id: data.device_id,
                text: data.text,
                is_emergency: data.is_emergency,
                confidence: data.confidence
            });
            
            // 保存到数据库
            const eventId = await saveEvent(data);
            console.log(`💾 事件已保存到数据库，ID: ${eventId}`);
            
            // 广播给所有连接的前端客户端
            io.emit('new-event', {
                ...data,
                id: eventId
            });
            
        } catch (error) {
            console.error('处理事件失败:', error);
            socket.emit('error', { message: '处理事件失败' });
        }
    });
    
    // 处理断开连接
    socket.on('disconnect', () => {
        console.log(`❌ 客户端已断开: ${socket.id}`);
        connectedClients.delete(socket.id);
        
        // 通知所有客户端连接数更新
        io.emit('client-count-update', connectedClients.size);
    });
});

// 启动服务器
const PORT = process.env.PORT || 3001;

async function startServer() {
    try {
        // 初始化数据库
        await initDatabase();
        
        // 启动HTTP服务器
        server.listen(PORT, () => {
            console.log('='.repeat(60));
            console.log('🚀 服务器启动成功');
            console.log('='.repeat(60));
            console.log(`📡 WebSocket服务器: http://localhost:${PORT}`);
            console.log(`📡 REST API: http://localhost:${PORT}/api`);
            console.log('✅ 等待客户端连接...\n');
        });
        
        // 优雅关闭
        process.on('SIGINT', async () => {
            console.log('\n🛑 正在关闭服务器...');
            await closeDatabase();
            server.close(() => {
                console.log('✅ 服务器已关闭');
                process.exit(0);
            });
        });
        
    } catch (error) {
        console.error('❌ 服务器启动失败:', error);
        process.exit(1);
    }
}

startServer();
