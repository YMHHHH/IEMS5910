import { useState, useEffect, useRef, useCallback } from 'react';
import { io } from 'socket.io-client';

/**
 * Socket.io连接Hook
 * @param {string} serverUrl - 服务器地址
 * @returns {Object} {socket, connected, addEventListener, removeEventListener}
 */
export function useSocket(serverUrl) {
    const [connected, setConnected] = useState(false);
    const socketRef = useRef(null);
    const listenersRef = useRef(new Map());

    useEffect(() => {
        // 创建socket连接
        const socket = io(serverUrl, {
            transports: ['websocket', 'polling'],
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: Infinity
        });

        socketRef.current = socket;

        // 连接成功
        socket.on('connect', () => {
            console.log('✅ Socket.io已连接');
            setConnected(true);
        });

        // 断开连接
        socket.on('disconnect', () => {
            console.log('❌ Socket.io已断开');
            setConnected(false);
        });

        // 连接错误
        socket.on('connect_error', (error) => {
            console.error('❌ Socket.io连接错误:', error);
            setConnected(false);
        });

        // 重新连接
        socket.on('reconnect', (attemptNumber) => {
            console.log(`✅ Socket.io重连成功 (尝试次数: ${attemptNumber})`);
            setConnected(true);
        });

        // 注册所有监听器
        listenersRef.current.forEach((handler, event) => {
            socket.on(event, handler);
        });

        // 清理函数
        return () => {
            // 移除所有监听器
            listenersRef.current.forEach((handler, event) => {
                socket.off(event, handler);
            });
            listenersRef.current.clear();
            socket.disconnect();
        };
    }, [serverUrl]);

    // 添加事件监听器
    const addEventListener = useCallback((event, handler) => {
        if (socketRef.current) {
            socketRef.current.on(event, handler);
            listenersRef.current.set(event, handler);
        }
    }, []);

    // 移除事件监听器
    const removeEventListener = useCallback((event) => {
        if (socketRef.current) {
            const handler = listenersRef.current.get(event);
            if (handler) {
                socketRef.current.off(event, handler);
                listenersRef.current.delete(event);
            }
        }
    }, []);

    return {
        socket: socketRef.current,
        connected,
        addEventListener,
        removeEventListener
    };
}
