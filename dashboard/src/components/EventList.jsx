import React from 'react';
import EventCard from './EventCard';

/**
 * 事件列表组件
 */
function EventList({ events }) {
    if (events.length === 0) {
        return (
            <div style={{
                padding: '40px',
                textAlign: 'center',
                color: '#999'
            }}>
                No events recorded yet.
            </div>
        );
    }

    return (
        <div style={{ padding: '20px' }}>
            {events.map((event) => (
                <EventCard key={event.id || `${event.timestamp}-${event.device_id}`} event={event} />
            ))}
        </div>
    );
}

export default EventList;
