#!/usr/bin/env python3
"""
音频录制模块
持续监听麦克风，检测语音活动并录制音频
"""

import wave
import tempfile
import os
import numpy as np
import threading
import queue

try:
    import pyaudio
    PYTHONAUDIO_AVAILABLE = True
except ImportError:
    PYTHONAUDIO_AVAILABLE = False

class AudioRecorder:
    """音频录制器 - 持续监听模式"""
    
    def __init__(self, sample_rate=16000, channels=1, chunk_size=1024, 
                 silence_threshold=500, min_audio_duration=1.0, max_audio_duration=5.0):
        """
        初始化音频录制器
        :param sample_rate: 采样率（Whisper推荐16000）
        :param channels: 声道数（1=单声道）
        :param chunk_size: 音频块大小
        :param silence_threshold: 静音阈值（音量低于此值视为静音）
        :param min_audio_duration: 最小录音时长（秒）
        :param max_audio_duration: 最大录音时长（秒）
        """
        if not PYTHONAUDIO_AVAILABLE:
            raise ImportError("pyaudio未安装，请运行: pip install pyaudio")
        
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.silence_threshold = silence_threshold
        self.min_audio_duration = min_audio_duration
        self.max_audio_duration = max_audio_duration
        
        self.audio = pyaudio.PyAudio()
        self.is_listening = False
        self.audio_queue = queue.Queue()
        
        # 列出可用的音频输入设备
        self._list_devices()
    
    def _list_devices(self):
        """列出可用的音频输入设备"""
        print("可用的音频输入设备:")
        print("-" * 50)
        device_count = self.audio.get_device_count()
        default_input = self.audio.get_default_input_device_info()
        
        for i in range(device_count):
            try:
                info = self.audio.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    marker = " (默认)" if info['index'] == default_input['index'] else ""
                    print(f"  [{info['index']}] {info['name']}{marker}")
            except:
                pass
        print("-" * 50)
        print(f"使用默认设备: {default_input['name']}\n")
    
    def _calculate_volume(self, audio_data):
        """计算音频音量（RMS）"""
        try:
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            if audio_np.size == 0:
                return 0
            # 使用浮点进行计算以避免溢出，并防止 NaN/Inf
            x = audio_np.astype(np.float32)
            rms = float(np.sqrt(np.mean(x * x)))
            if not np.isfinite(rms):
                return 0
            return int(rms)
        except Exception:
            return 0
    
    def _is_silence(self, audio_data):
        """判断是否为静音"""
        volume = self._calculate_volume(audio_data)
        return volume < self.silence_threshold
    
    def start_listening(self, callback):
        """
        开始持续监听麦克风
        :param callback: 当检测到语音并录制完成后，调用 callback(audio_file_path)
        """
        if self.is_listening:
            return
        
        self.is_listening = True
        self.callback = callback
        
        def listen_thread():
            """监听线程 - 持续监听并检测语音活动"""
            stream = None
            try:
                stream = self.audio.open(
                    format=pyaudio.paInt16,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    frames_per_buffer=self.chunk_size,
                    stream_callback=self._audio_callback
                )
                
                stream.start_stream()
                print(f"🎤 开始持续监听麦克风...")
                print(f"   采样率: {self.sample_rate} Hz")
                print(f"   静音阈值: {self.silence_threshold}")
                print(f"   检测到语音时自动录制并识别\n")
                
                # VAD状态
                audio_buffer = []
                is_recording = False
                silence_count = 0
                max_silence_chunks = int(self.sample_rate / self.chunk_size * 1.0)  # 1秒静音视为结束
                min_chunks = int(self.sample_rate / self.chunk_size * self.min_audio_duration)
                max_chunks = int(self.sample_rate / self.chunk_size * self.max_audio_duration)
                
                # 持续监听
                while self.is_listening:
                    try:
                        # 从队列获取音频块
                        try:
                            audio_chunk = self.audio_queue.get(timeout=0.1)
                        except queue.Empty:
                            # 如果正在录音但没有新数据，检查是否应该结束录音
                            if is_recording:
                                silence_count += 1
                                if silence_count >= max_silence_chunks and len(audio_buffer) >= min_chunks:
                                    # 结束录音
                                    is_recording = False
                                    audio_data = b''.join(audio_buffer)
                                    audio_buffer = []
                                    silence_count = 0
                                    
                                    # 保存并处理
                                    temp_fd, temp_file = tempfile.mkstemp(suffix='.wav')
                                    os.close(temp_fd)
                                    self._save_audio(audio_data, temp_file)
                                    
                                    if self.callback:
                                        self.callback(temp_file)
                            continue
                        
                        # 检测语音活动
                        if not self._is_silence(audio_chunk):
                            # 检测到语音
                            if not is_recording:
                                # 开始新录音
                                is_recording = True
                                audio_buffer = [audio_chunk]
                                silence_count = 0
                            else:
                                # 继续录音
                                audio_buffer.append(audio_chunk)
                                silence_count = 0
                                
                                # 检查是否达到最大长度
                                if len(audio_buffer) >= max_chunks:
                                    # 强制结束录音
                                    is_recording = False
                                    audio_data = b''.join(audio_buffer)
                                    audio_buffer = []
                                    
                                    # 保存并处理
                                    temp_fd, temp_file = tempfile.mkstemp(suffix='.wav')
                                    os.close(temp_fd)
                                    self._save_audio(audio_data, temp_file)
                                    
                                    if self.callback:
                                        self.callback(temp_file)
                        else:
                            # 静音
                            if is_recording:
                                # 正在录音中，继续收集（可能有短暂停顿）
                                audio_buffer.append(audio_chunk)
                                silence_count += 1
                                
                                # 如果静音时间过长，结束录音
                                if silence_count >= max_silence_chunks:
                                    if len(audio_buffer) >= min_chunks:
                                        # 结束录音
                                        is_recording = False
                                        audio_data = b''.join(audio_buffer)
                                        audio_buffer = []
                                        silence_count = 0
                                        
                                        # 保存并处理
                                        temp_fd, temp_file = tempfile.mkstemp(suffix='.wav')
                                        os.close(temp_fd)
                                        self._save_audio(audio_data, temp_file)
                                        
                                        if self.callback:
                                            self.callback(temp_file)
                                    else:
                                        # 录音太短，丢弃
                                        audio_buffer = []
                                        silence_count = 0
                                        is_recording = False
                                
                    except Exception as e:
                        print(f"❌ 处理音频时出错: {e}")
                        # 重置录音状态
                        audio_buffer = []
                        is_recording = False
                        silence_count = 0
                
            except Exception as e:
                print(f"❌ 监听失败: {e}")
            finally:
                if stream:
                    stream.stop_stream()
                    stream.close()
        
        # 启动监听线程
        self.listen_thread = threading.Thread(target=listen_thread, daemon=True)
        self.listen_thread.start()
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """音频流回调函数 - 将音频数据放入缓冲区"""
        if status:
            print(f"⚠️  音频流状态: {status}")
        
        if self.is_listening:
            # 简单地将所有音频数据放入缓冲区，由监听线程处理VAD
            try:
                self.audio_queue.put_nowait(in_data)
            except queue.Full:
                pass  # 队列满，丢弃旧数据
        
        return (None, pyaudio.paContinue)
    
    def _save_audio(self, audio_data, output_file):
        """保存音频数据为WAV文件"""
        with wave.open(output_file, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data)
    
    def stop_listening(self):
        """停止监听"""
        self.is_listening = False
        if hasattr(self, 'listen_thread'):
            self.listen_thread.join(timeout=2)
    
    def close(self):
        """关闭音频录制器"""
        self.stop_listening()
        if hasattr(self, 'audio'):
            self.audio.terminate()