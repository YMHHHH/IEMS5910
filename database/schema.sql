-- Database schema for the Elderly Voice Emergency Detection System
-- Create the database if it does not exist
CREATE DATABASE IF NOT EXISTS elderly_voice_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE elderly_voice_system;

-- Voice events table
CREATE TABLE IF NOT EXISTS voice_events (
    id INT PRIMARY KEY AUTO_INCREMENT,
    device_id VARCHAR(50) NOT NULL COMMENT 'Device identifier',
    text TEXT NOT NULL COMMENT 'Recognized text content',
    is_emergency BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Whether this is an emergency event',
    confidence DECIMAL(3,2) NOT NULL COMMENT 'Recognition confidence (0.00-1.00)',
    timestamp DATETIME NOT NULL COMMENT 'Event timestamp',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation time',
    
    -- Indexes
    INDEX idx_device_id (device_id),
    INDEX idx_is_emergency (is_emergency),
    INDEX idx_timestamp (timestamp),
    INDEX idx_device_timestamp (device_id, timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Voice event records table';
