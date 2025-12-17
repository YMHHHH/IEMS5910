/**
 * MySQL数据库操作模块
 * 封装数据库连接和CRUD操作
 */

const mysql = require('mysql2/promise');
require('dotenv').config();

let pool = null;

/**
 * 初始化数据库连接池
 */
async function initDatabase() {
    try {
        pool = mysql.createPool({
            host: process.env.DB_HOST || 'localhost',
            port: parseInt(process.env.DB_PORT) || 3306,
            user: process.env.DB_USER || 'root',
            password: process.env.DB_PASSWORD || '',
            database: process.env.DB_NAME || 'elderly_voice_system',
            waitForConnections: true,
            connectionLimit: 10,
            queueLimit: 0
        });
        
        // 测试连接
        const connection = await pool.getConnection();
        console.log('✅ 数据库连接成功');
        connection.release();
        
        return true;
    } catch (error) {
        console.error('❌ 数据库连接失败:', error.message);
        throw error;
    }
}

/**
 * 将ISO 8601时间戳转换为MySQL DATETIME格式
 * @param {string} isoString - ISO 8601格式的时间字符串 (如 '2025-10-29T18:59:48Z')
 * @returns {string} MySQL DATETIME格式 (如 '2025-10-29 18:59:48')
 */
function convertTimestampForMySQL(isoString) {
    if (!isoString) {
        // 如果没有提供时间戳，使用当前时间
        return new Date().toISOString().replace('T', ' ').substring(0, 19);
    }
    
    try {
        // 将ISO 8601格式转换为MySQL DATETIME格式
        // 例如: '2025-10-29T18:59:48Z' -> '2025-10-29 18:59:48'
        const date = new Date(isoString);
        const mysqlDatetime = date.toISOString()
            .replace('T', ' ')
            .substring(0, 19);
        return mysqlDatetime;
    } catch (error) {
        // 如果转换失败，使用当前时间
        console.warn('时间戳转换失败，使用当前时间:', error);
        return new Date().toISOString().replace('T', ' ').substring(0, 19);
    }
}

/**
 * 保存事件到数据库
 * @param {Object} event - 事件对象
 * @returns {Promise<number>} 插入的ID
 */
async function saveEvent(event) {
    if (!pool) {
        throw new Error('数据库未初始化');
    }
    
    try {
        // 转换时间戳格式为MySQL DATETIME格式
        const mysqlTimestamp = convertTimestampForMySQL(event.timestamp);
        
        const [result] = await pool.execute(
            `INSERT INTO voice_events (device_id, text, is_emergency, confidence, timestamp)
             VALUES (?, ?, ?, ?, ?)`,
            [
                event.device_id,
                event.text,
                event.is_emergency ? 1 : 0,
                event.confidence,
                mysqlTimestamp
            ]
        );
        
        return result.insertId;
    } catch (error) {
        console.error('保存事件失败:', error);
        throw error;
    }
}

/**
 * 查询历史事件
 * @param {number} limit - 返回数量限制
 * @param {number} offset - 偏移量
 * @returns {Promise<Array>} 事件数组
 */
async function getEvents(limit = 100, offset = 0) {
    if (!pool) {
        throw new Error('数据库未初始化');
    }
    
    try {
        // 确保 limit / offset 为安全的整数，避免将非数字或字符串传入预处理语句
        let safeLimit = Number(limit);
        let safeOffset = Number(offset);
        if (!Number.isFinite(safeLimit) || safeLimit <= 0) safeLimit = 100;
        if (!Number.isFinite(safeOffset) || safeOffset < 0) safeOffset = 0;
        // 限制最大返回数量，防止滥用
        safeLimit = Math.min(Math.max(Math.floor(safeLimit), 1), 1000);
        safeOffset = Math.max(Math.floor(safeOffset), 0);

        // 为避免某些 MySQL 驱动/服务器在 prepared statements 中对 LIMIT/OFFSET 占位符的兼容性问题，
        // 这里将安全的整数直接插入 SQL 字符串（已经过验证且为整数），而不是作为占位符绑定参数。
        const sql = `SELECT id, device_id, text, is_emergency, confidence, timestamp, created_at
             FROM voice_events
             ORDER BY timestamp DESC
             LIMIT ${safeLimit} OFFSET ${safeOffset}`;

        const [rows] = await pool.query(sql);
        
        // 转换布尔值
        return rows.map(row => ({
            ...row,
            is_emergency: Boolean(row.is_emergency)
        }));
    } catch (error) {
        console.error('查询事件失败:', error);
        throw error;
    }
}

/**
 * 关闭数据库连接
 */
async function closeDatabase() {
    if (pool) {
        await pool.end();
        pool = null;
        console.log('✅ 数据库连接已关闭');
    }
}

module.exports = {
    initDatabase,
    saveEvent,
    getEvents,
    closeDatabase
};
