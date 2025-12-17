#!/usr/bin/env python3
"""
配置管理模块
读取环境变量和默认配置
"""

import os
from pathlib import Path

def get_config():
    """
    读取配置信息
    返回配置字典
    """
    # 获取项目根目录
    base_dir = Path(__file__).parent
    
    config = {
        # 服务器配置
        'SERVER_URL': os.getenv('SERVER_URL', 'http://localhost:3001'),
        
        # 设备配置
        'DEVICE_ID': os.getenv('DEVICE_ID', 'elder-device-01'),
        
        # Whisper 模型配置（使用 openai-whisper）
        'WHISPER_MODEL': os.getenv('WHISPER_MODEL', 'base'),
        # 识别任务：'en' 或 'zh'
        'WHISPER_TASK': os.getenv('WHISPER_TASK', 'en'),
        
        # 音频输入模式（默认使用麦克风输入，设置为'true'则使用模拟音频文件）
        'MOCK_AUDIO': os.getenv('MOCK_AUDIO', 'false').lower() == 'true',
        
        # 音频样本目录
        'AUDIO_SAMPLES_DIR': os.getenv('AUDIO_SAMPLES_DIR', str(base_dir / 'audio_samples')),
        
        # 事件发送间隔（秒）
        'MIN_INTERVAL': float(os.getenv('MIN_INTERVAL', '3')),
        'MAX_INTERVAL': float(os.getenv('MAX_INTERVAL', '8')),
        
        # 麦克风监听参数（仅在使用麦克风时有效）
        'SILENCE_THRESHOLD': int(os.getenv('SILENCE_THRESHOLD', '500')),  # 静音阈值
        'MIN_AUDIO_DURATION': float(os.getenv('MIN_AUDIO_DURATION', '1.0')),  # 最小录音时长（秒）
        'MAX_AUDIO_DURATION': float(os.getenv('MAX_AUDIO_DURATION', '5.0')),  # 最大录音时长（秒）
    }
    
    return config
