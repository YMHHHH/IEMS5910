#!/usr/bin/env python3
"""
老年人语音呼救检测系统 - 端侧设备模拟器
使用Whisper进行离线语音识别，通过WebSocket发送事件到服务器
支持麦克风输入和模拟音频文件两种模式
"""

import socketio
import time
import random
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from config import get_config
from whisper_handler import WhisperHandler

# 尝试导入音频录制模块
try:
    from audio_recorder import AudioRecorder
    AUDIO_RECORDER_AVAILABLE = True
except ImportError:
    AUDIO_RECORDER_AVAILABLE = False
    print("⚠️  音频录制模块未加载，将仅支持模拟音频文件模式")

# Socket.IO客户端
sio = socketio.Client()

# 全局变量
whisper_handler = None
config = None
audio_files = []
audio_recorder = None

@sio.on('connect')
def on_connect():
    """连接成功回调"""
    print(f'✅ 已连接到服务器: {config["SERVER_URL"]}')
    print(f'📡 设备ID: {config["DEVICE_ID"]}')

@sio.on('disconnect')
def on_disconnect():
    """断开连接回调"""
    print('❌ 与服务器断开连接')

@sio.on('connect_error')
def on_connect_error(error):
    """连接错误回调"""
    print(f'❌ 连接错误: {error}')
    print('⚠️  请确保服务器正在运行')

def load_audio_files():
    """加载音频文件列表"""
    audio_dir = Path(config['AUDIO_SAMPLES_DIR'])
    if not audio_dir.exists():
        print(f'⚠️  音频目录不存在: {audio_dir}')
        return []
    
    # 支持常见音频格式
    extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
    files = []
    for ext in extensions:
        files.extend(list(audio_dir.glob(f'*{ext}')))
    
    if not files:
        print(f'⚠️  音频目录中没有找到音频文件: {audio_dir}')
        print('💡 提示：请将测试音频文件放入 audio_samples/ 目录')
    
    return [str(f) for f in files]

def process_audio_file(audio_path):
    """处理音频识别和事件发送（用于回调）"""
    try:
        if not os.path.exists(audio_path):
            return
        
        # Whisper识别
        result = whisper_handler.transcribe(audio_path)
        text = result['text']
        confidence = result['confidence']
        
        print(f'🎤 识别结果: "{text}" (置信度: {confidence})')
        
        # 检测是否为紧急事件
        is_emergency = whisper_handler.detect_emergency(text)
        
        # 构建事件对象
        event = {
            'device_id': config['DEVICE_ID'],
            'text': text,
            'is_emergency': is_emergency,
            'confidence': confidence,
            'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        
        # 发送事件
        if sio.connected:
            sio.emit('voice-event', event)
            status = '🚨 紧急' if is_emergency else '📝 普通'
            print(f'{status} 事件已发送: {text}\n')
        else:
            print('⚠️  未连接到服务器，事件未发送')
        
        # 清理临时文件
        try:
            os.remove(audio_path)
        except:
            pass
    
    except Exception as e:
        print(f'❌ 处理音频时出错: {e}')
        # 清理临时文件
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except:
            pass

def main():
    """主函数"""
    global whisper_handler, config, audio_files, audio_recorder
    
    print('=' * 60)
    print('🎤 老年人语音呼救检测系统 - 端侧设备模拟器')
    print('=' * 60)
    
    # 加载配置
    config = get_config()
    print(f'📋 配置加载完成')
    print(f'   服务器地址: {config["SERVER_URL"]}')
    print(f'   设备ID: {config["DEVICE_ID"]}')
    # 打印模型配置信息（使用原生 openai-whisper）
    print(f'   Whisper模型: {config["WHISPER_MODEL"]}')
    print(f'   识别任务: {config.get("WHISPER_TASK", "en")}')
    print(f'   音频模式: {"模拟音频文件" if config["MOCK_AUDIO"] else "真实麦克风输入"}')
    
    # 初始化Whisper
    try:
        # 传入整个 config，以便 WhisperHandler 决定使用 RKNN 还是原生 whisper
        whisper_handler = WhisperHandler(config)
    except Exception as e:
        print(f'❌ Whisper初始化失败: {e}')
        return
    
    # 连接到服务器
    try:
        print(f'\n🔌 正在连接到服务器: {config["SERVER_URL"]}...')
        sio.connect(config['SERVER_URL'])
        time.sleep(1)  # 等待连接建立
    except Exception as e:
        print(f'❌ 连接失败: {e}')
        print('💡 请确保服务器正在运行')
        return
    
    # 根据模式启动不同的处理流程
    if config['MOCK_AUDIO']:
        # 模拟音频文件模式
        audio_files = load_audio_files()
        if not audio_files:
            print('❌ 未找到音频文件，程序退出')
            print('💡 请在 audio_samples/ 目录中添加测试音频文件')
            return
        print(f'📁 找到 {len(audio_files)} 个音频文件')
        print('🔄 开始模拟音频文件循环...')
        print(f'   间隔: {config["MIN_INTERVAL"]}-{config["MAX_INTERVAL"]} 秒\n')
        
        try:
            while True:
                if sio.connected:
                    # 随机选择音频文件并处理
                    audio_path = random.choice(audio_files)
                    print(f'📂 处理音频文件: {os.path.basename(audio_path)}')
                    process_audio_file(audio_path)
                    
                    # 随机等待间隔
                    interval = random.uniform(config['MIN_INTERVAL'], config['MAX_INTERVAL'])
                    time.sleep(interval)
                else:
                    print('⚠️  连接断开，尝试重连...')
                    try:
                        sio.connect(config['SERVER_URL'])
                        time.sleep(2)
                    except:
                        print('❌ 重连失败，5秒后重试...')
                        time.sleep(5)
        
        except KeyboardInterrupt:
            print('\n\n🛑 收到中断信号，正在关闭...')
            if sio.connected:
                sio.disconnect()
            print('✅ 程序已退出')
    
    else:
        # 真实麦克风持续监听模式
        if not AUDIO_RECORDER_AVAILABLE:
            print('❌ 音频录制模块不可用')
            print('💡 请安装pyaudio: pip install pyaudio')
            return
        
        try:
            print('\n🎤 初始化音频录制器（持续监听模式）...')
            audio_recorder = AudioRecorder(
                sample_rate=16000,
                channels=1,
                silence_threshold=config.get('SILENCE_THRESHOLD', 500),
                min_audio_duration=config.get('MIN_AUDIO_DURATION', 1.0),
                max_audio_duration=config.get('MAX_AUDIO_DURATION', 5.0)
            )
            print('✅ 音频录制器初始化成功')
            
            # 开始持续监听
            audio_recorder.start_listening(process_audio_file)
            
            print('\n💡 系统已启动，24小时持续监听中...')
            print('💡 检测到语音时会自动识别并发送事件')
            print('💡 按 Ctrl+C 停止监听\n')
            
            # 主循环：保持程序运行
            try:
                while True:
                    if not sio.connected:
                        print('⚠️  连接断开，尝试重连...')
                        try:
                            sio.connect(config['SERVER_URL'])
                            time.sleep(2)
                        except:
                            print('❌ 重连失败，5秒后重试...')
                            time.sleep(5)
                    else:
                        time.sleep(1)  # 每1秒检查一次连接状态
            
            except KeyboardInterrupt:
                print('\n\n🛑 收到中断信号，正在关闭...')
                audio_recorder.stop_listening()
                if sio.connected:
                    sio.disconnect()
                print('✅ 程序已退出')
        
        except Exception as e:
            print(f'❌ 音频录制器初始化失败: {e}')
            print('💡 请检查麦克风权限和pyaudio安装')
            print('💡 macOS需要授予终端或Python应用麦克风权限')
            return

if __name__ == '__main__':
    main()
