import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useSocket } from './hooks/useSocket';
import StatusBar from './components/StatusBar';
import EventList from './components/EventList';

// 从环境变量读取服务器地址，如果没有则使用 localhost
// 支持 ngrok URL，例如: https://xxxx-xx-xx-xx-xx.ngrok-free.app
const SERVER_URL = import.meta.env.VITE_SERVER_URL || 'http://localhost:3001';

function App() {
    const [events, setEvents] = useState([]);
    const [deviceCount, setDeviceCount] = useState(0);
    const [emergencyActive, setEmergencyActive] = useState(false);
    const alarmIntervalRef = useRef(null);
    const audioCtxRef = useRef(null);
    const gainNodeRef = useRef(null);
    const { connected, addEventListener, removeEventListener } = useSocket(SERVER_URL);

    // 加载历史事件
    const loadHistoryEvents = useCallback(async () => {
        try {
            const response = await fetch(`${SERVER_URL}/api/events?limit=100`);
            if (response.ok) {
                const data = await response.json();
                setEvents(data);
            } else {
                console.error('加载历史事件失败');
            }
        } catch (error) {
            console.error('加载历史事件出错:', error);
        }
    }, []);

    // 加载统计信息
    const loadStats = useCallback(async () => {
        try {
            const response = await fetch(`${SERVER_URL}/api/stats`);
            if (response.ok) {
                const data = await response.json();
                setDeviceCount(data.connectedClients || 0);
            }
        } catch (error) {
            console.error('加载统计信息出错:', error);
        }
    }, []);

    // 初始化加载
    useEffect(() => {
        loadHistoryEvents();
        loadStats();
    }, [loadHistoryEvents, loadStats]);

    // 监听新事件
    useEffect(() => {
        if (!connected) return;

        const handleNewEvent = (newEvent) => {
            console.log('收到新事件:', newEvent);
            setEvents((prev) => [newEvent, ...prev]);

            // 若是紧急事件，触发报警音与闪烁
            if (newEvent && newEvent.is_emergency) {
                // 开始报警（如果尚未在报警）
                if (!emergencyActive) {
                    setEmergencyActive(true);
                }
                startAlarm();
            }
        };

        const handleClientCountUpdate = (count) => {
            setDeviceCount(count);
        };

        addEventListener('new-event', handleNewEvent);
        addEventListener('client-count-update', handleClientCountUpdate);

        return () => {
            removeEventListener('new-event');
            removeEventListener('client-count-update');
        };
    }, [connected, addEventListener, removeEventListener]);

    // 当用户点击静音或清除报警时，停止声音并关闭闪烁
    const stopAlarm = () => {
        // stop WebAudio oscillator pattern
        if (alarmIntervalRef.current) {
            clearInterval(alarmIntervalRef.current);
            alarmIntervalRef.current = null;
        }
        if (gainNodeRef.current) {
            try { gainNodeRef.current.gain.cancelScheduledValues(0); gainNodeRef.current.gain.setValueAtTime(0, audioCtxRef.current.currentTime); } catch (e) {}
        }
        if (audioCtxRef.current) {
            try { audioCtxRef.current.close(); } catch (e) {}
            audioCtxRef.current = null;
        }
        setEmergencyActive(false);
    };

    // 启动基于 Web Audio 的报警（反复哔哔声）
    const startAlarm = () => {
        try {
            if (!window.AudioContext && !window.webkitAudioContext) return;
            if (audioCtxRef.current == null) {
                const AudioContext = window.AudioContext || window.webkitAudioContext;
                const ctx = new AudioContext();
                audioCtxRef.current = ctx;
                const gain = ctx.createGain();
                gain.gain.value = 0;
                gain.connect(ctx.destination);
                gainNodeRef.current = gain;

                // 创建振荡器并控制音量周期性触发（哔哔）
                const osc = ctx.createOscillator();
                osc.type = 'sine';
                osc.frequency.value = 880;
                osc.connect(gain);
                osc.start();

                // 每 600ms 做一次短促音
                alarmIntervalRef.current = setInterval(() => {
                    if (!gainNodeRef.current || !audioCtxRef.current) return;
                    const now = audioCtxRef.current.currentTime;
                    try {
                        gainNodeRef.current.gain.cancelScheduledValues(now);
                        gainNodeRef.current.gain.setValueAtTime(0, now);
                        gainNodeRef.current.gain.linearRampToValueAtTime(0.5, now + 0.02);
                        gainNodeRef.current.gain.linearRampToValueAtTime(0.0, now + 0.18);
                    } catch (e) {
                        // ignore scheduling errors
                    }
                }, 600);
            }
        } catch (e) {
            console.error('无法启动报警音', e);
        }
    };

    // 清理（卸载时停止报警）
    useEffect(() => {
        return () => {
            if (alarmIntervalRef.current) {
                clearInterval(alarmIntervalRef.current);
                alarmIntervalRef.current = null;
            }
            if (audioCtxRef.current) {
                try { audioCtxRef.current.close(); } catch (e) {}
                audioCtxRef.current = null;
            }
        };
    }, []);

    return (
        <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
            <header className={emergencyActive ? 'alarm-blink-header' : ''} style={{
                background: '#2196f3',
                color: '#fff',
                padding: '20px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
                <h1 style={{ fontSize: '24px', fontWeight: 'bold' }}>
                    Elderly Emergency Voice Detection System
                </h1>
                <p style={{ fontSize: '14px', marginTop: '8px', opacity: 0.9 }}>
                    Real-Time Monitoring Dashboard
                </p>
                {/* 开发用：模拟紧急事件按钮（便于测试） */}
                <div style={{ marginTop: 8 }}>
                    <button style={{ padding: '6px 10px', borderRadius: 6, border: 'none', background: '#ff7043', color: '#fff', cursor: 'pointer' }} onClick={() => { setEmergencyActive(true); startAlarm(); }}>
                        Simulate Emergency
                    </button>
                </div>
            </header>

            {/* 全屏闪烁覆盖层（仅视觉提示） */}
            {emergencyActive && <div className="alarm-overlay" aria-hidden="true"></div>}

            {/* 静音/关闭按钮 */}
            {emergencyActive && (
                <div className="alarm-control">
                    <span className="alarm-pill">🚨 EMERGENCY</span>
                    <button className="alarm-button" onClick={stopAlarm}>Silence Alarm</button>
                </div>
            )}

            <StatusBar connected={connected} deviceCount={deviceCount} />

            <main>
                <div style={{
                    padding: '20px',
                    background: '#fff',
                    margin: '20px',
                    borderRadius: '8px',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}>
                    <h2 style={{
                        fontSize: '20px',
                        fontWeight: 'bold',
                        marginBottom: '16px',
                        color: '#333'
                    }}>
                        Event Logs
                    </h2>
                    <EventList events={events} />
                </div>
            </main>
        </div>
    );
}

export default App;
