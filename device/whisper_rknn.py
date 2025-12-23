#!/usr/bin/env python3
"""
RKNN版本的Whisper语音识别处理器
用于替换原生Whisper，在Rockchip设备上运行
"""

import numpy as np
import scipy
import os
import wave
import warnings

# 抑制警告
warnings.filterwarnings("ignore", category=UserWarning)

try:
    from rknn.api import RKNN
    RKNN_AVAILABLE = True
except ImportError:
    RKNN = None
    RKNN_AVAILABLE = False
    print("⚠️  警告: 未安装rknn库，请确保在RKNN设备上运行")

try:
    import torch
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    F = None
    TORCH_AVAILABLE = False
    print("⚠️  警告: 未安装torch，部分功能可能受限")

# Whisper常量
SAMPLE_RATE = 16000
N_FFT = 400
HOP_LENGTH = 160
CHUNK_LENGTH = 20
N_SAMPLES = CHUNK_LENGTH * SAMPLE_RATE
MAX_LENGTH = CHUNK_LENGTH * 100
N_MELS = 80

class WhisperHandlerRKNN:
    """使用RKNN模型进行语音识别的处理器"""

    def __init__(self, config):
        """
        初始化RKNN Whisper处理器
        :param config: 配置字典，包含以下键：
            - ENCODER_MODEL_PATH: 编码器模型路径
            - DECODER_MODEL_PATH: 解码器模型路径
            - VOCAB_PATH: 词汇表路径
            - TASK: 'en'或'zh'，识别任务
            - RKNN_TARGET: RKNN目标平台，如'rk3566'
            - RKNN_DEVICE_ID: 设备ID
        """
        self.config = config
        self.emergency_keywords = self._load_keywords()
        
        if not RKNN_AVAILABLE:
            raise RuntimeError('未检测到RKNN库，请确保在RKNN设备上运行')
        
        # 从配置中获取模型路径
        encoder_path = config.get('ENCODER_MODEL_PATH', '../model/encoder.rknn')
        decoder_path = config.get('DECODER_MODEL_PATH', '../model/decoder.rknn')
        vocab_path = config.get('VOCAB_PATH', '../model/vocab_zh.txt')
        task = config.get('TASK', 'zh')
        target = config.get('RKNN_TARGET', 'rk3566')
        device_id = config.get('RKNN_DEVICE_ID', None)
        
        print(f'🎯 正在加载RKNN Whisper模型...')
        print(f'   编码器: {encoder_path}')
        print(f'   解码器: {decoder_path}')
        print(f'   任务: {task}')
        
        try:
            # 加载词汇表
            self.vocab = self._read_vocab(vocab_path)
            
            # 设置任务代码
            if task == "en":
                self.task_code = 50259  # 英语任务
            elif task == "zh":
                self.task_code = 50260  # 中文任务
            else:
                print(f"⚠️  警告: 未知任务 '{task}'，默认为中文")
                self.task_code = 50260
            
            # 初始化模型
            print('   加载编码器模型...')
            self.encoder_model = self._init_model(encoder_path, target, device_id)
            print('   加载解码器模型...')
            self.decoder_model = self._init_model(decoder_path, target, device_id)
            
            # 加载mel滤波器
            self.mel_filters_data = self._load_mel_filters()
            
            print('✅ RKNN模型加载完成')
            
        except Exception as e:
            raise RuntimeError(f'RKNN模型初始化失败: {e}')

    def _load_keywords(self):
        """加载紧急关键词"""
        return [
            'help',
            '救命',
            '救',
        ]

    def _init_model(self, model_path, target=None, device_id=None):
        """初始化RKNN模型"""
        model = RKNN()
        
        # 检查模型文件是否存在
        if not os.path.exists(model_path):
            raise FileNotFoundError(f'模型文件不存在: {model_path}')
        
        # 加载RKNN模型
        ret = model.load_rknn(model_path)
        if ret != 0:
            raise RuntimeError(f'加载RKNN模型 "{model_path}" 失败!')
        
        # 初始化运行环境
        ret = model.init_runtime(target=target, device_id=device_id)
        if ret != 0:
            raise RuntimeError('初始化运行环境失败')
        
        return model

    def _read_vocab(self, vocab_path):
        """读取词汇表 - 修复版"""
        vocab = {}
        try:
            if not os.path.exists(vocab_path):
                print(f'⚠️  警告: 词汇表文件不存在 {vocab_path}')
                return self._create_basic_vocab()
            
            with open(vocab_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(' ')
                    if len(parts) < 2:
                        key = parts[0]
                        value = ""
                    else:
                        key, value = parts[0], ' '.join(parts[1:])
                    vocab[key] = value
            return vocab
        except Exception as e:
            print(f'⚠️  读取词汇表失败: {e}，使用内置基本词汇表')
            return self._create_basic_vocab()

    def _create_basic_vocab(self):
        """创建基本词汇表（用于测试）"""
        basic_vocab = {
            '50258': '',  # 开始token
            '50257': '',  # 结束token
            '50259': '',  # 英语任务
            '50260': '',  # 中文任务
            '50359': '',  # 语言token
            '50363': '',  # 转录token
        }
        
        # 添加一些常见字符
        for i in range(65, 91):  # A-Z
            basic_vocab[str(i)] = chr(i)
        for i in range(97, 123):  # a-z
            basic_vocab[str(i)] = chr(i)
        
        return basic_vocab

    def _load_mel_filters(self):
        """加载mel滤波器"""
        try:
            # 尝试从多个可能的位置查找mel滤波器文件
            possible_paths = [
                './model/mel_80_filters.txt',
                os.path.join(os.path.dirname(__file__), 'mel_80_filters.txt'),
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    print(f'   找到mel滤波器: {path}')
                    return np.loadtxt(path, dtype=np.float32).reshape((80, 201))
            
            # 如果找不到文件，创建默认的mel滤波器
            print('⚠️  警告: 未找到mel滤波器文件，使用默认值')
            return self._create_default_mel_filters()
        except Exception as e:
            print(f'⚠️  加载mel滤波器失败: {e}，使用默认值')
            return self._create_default_mel_filters()

    def _create_default_mel_filters(self):
        """创建默认的mel滤波器（简单版本）"""
        n_mels = 80
        n_fft = 400
        
        # 创建简单的mel滤波器
        filters = np.zeros((n_mels, n_fft // 2 + 1), dtype=np.float32)
        for i in range(n_mels):
            start = int(i * (n_fft // 2 + 1) / n_mels)
            end = int((i + 1) * (n_fft // 2 + 1) / n_mels)
            if start < end:
                filters[i, start:end] = 1.0
        
        return filters

    def _ensure_sample_rate(self, waveform, original_sample_rate, desired_sample_rate=16000):
        """确保采样率为目标采样率"""
        if original_sample_rate != desired_sample_rate:
            desired_length = int(round(float(len(waveform)) / original_sample_rate * desired_sample_rate))
            waveform = scipy.signal.resample(waveform, desired_length)
        return waveform

    def _pad_or_trim(self, audio_array):
        """填充或修剪音频数组到固定长度"""
        x_mel = np.zeros((N_MELS, MAX_LENGTH), dtype=np.float32)
        real_length = audio_array.shape[1] if audio_array.shape[1] <= MAX_LENGTH else MAX_LENGTH
        x_mel[:, :real_length] = audio_array[:, :real_length]
        return x_mel

    def _log_mel_spectrogram(self, audio, n_mels, padding=0):
        """计算对数梅尔频谱"""
        if TORCH_AVAILABLE:
            return self._log_mel_spectrogram_torch(audio, n_mels, padding)
        else:
            # 使用numpy/scipy实现简化版本
            return self._log_mel_spectrogram_numpy(audio, n_mels, padding)

    def _log_mel_spectrogram_torch(self, audio, n_mels, padding=0):
        """使用torch计算对数梅尔频谱"""
        if not torch.is_tensor(audio):
            audio = torch.from_numpy(audio)

        if padding > 0:
            audio = F.pad(audio, (0, padding))
        
        window = torch.hann_window(N_FFT)
        stft = torch.stft(audio, N_FFT, HOP_LENGTH, window=window, return_complex=True)
        magnitudes = stft[..., :-1].abs() ** 2

        filters = torch.from_numpy(self.mel_filters_data)
        mel_spec = filters @ magnitudes

        log_spec = torch.clamp(mel_spec, min=1e-10).log10()
        log_spec = torch.maximum(log_spec, log_spec.max() - 8.0)
        log_spec = (log_spec + 4.0) / 4.0
        return log_spec

    def _log_mel_spectrogram_numpy(self, audio, n_mels, padding=0):
        """使用numpy/scipy计算对数梅尔频谱（简化版本）"""
        import scipy.signal as sp
        
        if padding > 0:
            audio = np.pad(audio, (0, padding))
        
        # 使用scipy计算STFT
        f, t, Zxx = sp.stft(audio, fs=SAMPLE_RATE, nperseg=N_FFT, noverlap=N_FFT - HOP_LENGTH)
        magnitudes = np.abs(Zxx[:-1]) ** 2  # 去掉最后一个频率点
        
        # 应用mel滤波器
        mel_spec = self.mel_filters_data @ magnitudes
        
        # 对数变换
        log_spec = np.clip(mel_spec, a_min=1e-10, a_max=None)
        log_spec = np.log10(log_spec)
        log_spec = np.maximum(log_spec, log_spec.max() - 8.0)
        log_spec = (log_spec + 4.0) / 4.0
        
        return log_spec

    def _base64_decode(self, encoded_string):
        """Base64解码（用于中文结果）- 完整版"""
        if not encoded_string:
            return ""
        
        # 直接使用你提供的能工作的base64_decode函数
        def get_char_index(c):
            if 'A' <= c <= 'Z':
                return ord(c) - ord('A')
            elif 'a' <= c <= 'z':
                return ord(c) - ord('a') + (ord('Z') - ord('A') + 1)
            elif '0' <= c <= '9':
                return ord(c) - ord('0') + (ord('Z') - ord('A')) + (ord('z') - ord('a')) + 2
            elif c == '+':
                return 62
            elif c == '/':
                return 63
            else:
                return 0
        
        output_length = len(encoded_string) // 4 * 3
        decoded_string = bytearray(output_length)
        
        index = 0
        output_index = 0
        while index < len(encoded_string):
            if encoded_string[index] == '=':
                return " "
            
            first_byte = (get_char_index(encoded_string[index]) << 2) + ((get_char_index(encoded_string[index + 1]) & 0x30) >> 4)
            decoded_string[output_index] = first_byte
            
            if index + 2 < len(encoded_string) and encoded_string[index + 2] != '=':
                second_byte = ((get_char_index(encoded_string[index + 1]) & 0x0f) << 4) + ((get_char_index(encoded_string[index + 2]) & 0x3c) >> 2)
                decoded_string[output_index + 1] = second_byte
                
                if index + 3 < len(encoded_string) and encoded_string[index + 3] != '=':
                    third_byte = ((get_char_index(encoded_string[index + 2]) & 0x03) << 6) + get_char_index(encoded_string[index + 3])
                    decoded_string[output_index + 2] = third_byte
                    output_index += 3
                else:
                    output_index += 2
            else:
                output_index += 1
            
            index += 4
                
        return decoded_string.decode('utf-8', errors='replace')

    def _run_encoder(self, in_encoder):
        """运行编码器"""
        out_encoder = self.encoder_model.inference(inputs=[in_encoder])[0]
        return out_encoder

    def _run_decoder(self, tokens, out_encoder):
        """运行解码器"""
        out_decoder = self.decoder_model.inference([np.asarray([tokens], dtype="int64"), out_encoder])[0]
        return out_decoder

    def _decode_text(self, out_encoder):
        """解码生成文本 - 修复版"""
        end_token = 50257  # 结束token
        timestamp_begin = 50364  # 时间戳开始token (非常重要！)
        
        # 初始tokens: [开始token, 任务代码, 语言token, 转录token]
        tokens = [50258, self.task_code, 50359, 50363]
        
        max_tokens = 12
        tokens_str = ''
        pop_id = max_tokens
        
        # 填充tokens到初始长度
        tokens = tokens * int(max_tokens / 4)
        next_token = 50258  # 开始token
        
        while next_token != end_token:
            out_decoder = self._run_decoder(tokens, out_encoder)
            next_token = out_decoder[0, -1].argmax()
            next_token_str = self.vocab.get(str(next_token), "")
            
            tokens.append(next_token)
            
            # 如果是结束token，跳出循环
            if next_token == end_token:
                tokens.pop(-1)  # 移除刚添加的结束token
                break
            
            # 如果是时间戳token，跳过（不添加到输出文本）
            if next_token >= timestamp_begin:
                continue
            
            # 维护tokens列表长度
            if pop_id > 4:
                pop_id -= 1
            tokens.pop(pop_id)
            
            # 添加到输出文本
            tokens_str += next_token_str
        
        # 清理和格式化结果
        result = tokens_str.replace('\u0120', ' ').replace('<|endoftext|>', '').replace('\n', '')
        
        # 如果是中文任务，进行base64解码
        if self.task_code == 50260:  # 中文任务
            result = self._base64_decode(result)
        
        return result.strip()

    def transcribe(self, audio_path):
        """识别音频文件，返回 {'text': str, 'confidence': float}"""
        try:
            # 读取音频文件
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"音频文件不存在: {audio_path}")
            
            # 使用wave模块读取WAV文件
            with wave.open(audio_path, 'rb') as wf:
                sample_rate = wf.getframerate()
                n_frames = wf.getnframes()
                audio_data = wf.readframes(n_frames)
                
                # 转换为numpy数组
                audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            # 确保采样率为16000Hz
            if sample_rate != SAMPLE_RATE:
                audio_array = self._ensure_sample_rate(audio_array, sample_rate, SAMPLE_RATE)
            
            # 计算梅尔频谱
            audio_mel = self._log_mel_spectrogram(audio_array, N_MELS)
            
            # 转换为numpy数组
            if TORCH_AVAILABLE and isinstance(audio_mel, torch.Tensor):
                audio_mel = audio_mel.numpy()
            
            # 填充或修剪到固定长度
            x_mel = self._pad_or_trim(audio_mel)
            x_mel = np.expand_dims(x_mel, 0)  # 添加批次维度
            
            # 运行编码器
            out_encoder = self._run_encoder(x_mel)
            
            # 运行解码器生成文本
            text = self._decode_text(out_encoder)
            
            # 对于RKNN版本，暂时使用固定置信度
            # 在实际使用中，可以根据解码器的输出计算置信度
            confidence = 0.85
            
            return {'text': text, 'confidence': round(confidence, 2)}
            
        except Exception as e:
            print(f'❌ RKNN识别失败: {e}')
            # 返回空结果
            return {'text': '', 'confidence': 0.0}

    def detect_emergency(self, text):
        """检测是否为紧急事件"""
        if not text:
            return False
        tl = text.lower()
        for k in self.emergency_keywords:
            if k.lower() in tl:
                return True
        return False

    def release(self):
        """释放模型资源"""
        if hasattr(self, 'encoder_model'):
            self.encoder_model.release()
        if hasattr(self, 'decoder_model'):
            self.decoder_model.release()
        print('✅ RKNN模型已释放')