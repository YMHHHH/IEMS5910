import React from 'react';

/**
 * 状态栏组件
 * 显示连接状态和活跃设备数
 */
function StatusBar({ connected, deviceCount }) {
    return (
        <div style={{
            padding: '16px',
            background: '#fff',
            borderBottom: '1px solid #e0e0e0',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                }}>
                    <div style={{
                        width: '12px',
                        height: '12px',
                        borderRadius: '50%',
                        background: connected ? '#4caf50' : '#f44336'
                    }}></div>
                    <span style={{ fontSize: '14px', color: '#666' }}>
                        {connected ? 'Connected' : 'Disconnected'}
                    </span>
                </div>
            </div>
            <div style={{ fontSize: '14px', color: '#666' }}>
                Active Devices: <strong>{deviceCount}</strong>
            </div>
        </div>
    );
}

export default StatusBar;
