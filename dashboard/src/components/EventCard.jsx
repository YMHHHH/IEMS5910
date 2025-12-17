import React from 'react';

/**
 * 事件卡片组件
 */
function EventCard({ event }) {
    const formatTime = (timestamp) => {
        try {
            const date = new Date(timestamp);
            return date.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        } catch (e) {
            return timestamp;
        }
    };

    return (
        <div style={{
            padding: '16px',
            marginBottom: '12px',
            background: event.is_emergency ? '#fff3cd' : '#fff',
            border: `2px solid ${event.is_emergency ? '#ff9800' : '#e0e0e0'}`,
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                marginBottom: '8px'
            }}>
                <div>
                    <div style={{
                        display: 'inline-block',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: 'bold',
                        background: event.is_emergency ? '#ff5722' : '#2196f3',
                        color: '#fff',
                        marginRight: '8px'
                    }}>
                        {event.is_emergency ? '🚨 Emergency' : '📝 Normal'}
                    </div>
                    <span style={{ fontSize: '12px', color: '#666' }}>
                        device: {event.device_id}
                    </span>
                </div>
                <div style={{ fontSize: '12px', color: '#666' }}>
                    {formatTime(event.timestamp)}
                </div>
            </div>
            
            <div style={{
                fontSize: '16px',
                fontWeight: '500',
                marginBottom: '8px',
                color: '#333'
            }}>
                {event.text}
            </div>
            
            <div style={{ fontSize: '12px', color: '#888' }}>
                Confidence: {(event.confidence * 100).toFixed(1)}%
            </div>
        </div>
    );
}

export default EventCard;
