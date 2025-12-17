#!/usr/bin/env python3
"""
Whisper 处理器 — 仅使用 openai-whisper（原生 Whisper）进行推理。

此文件被精简以移除 RKNN/ONNX 支持，保持对原始项目的兼容性。
"""

import os
import ssl

try:
    import whisper
except Exception:
    whisper = None


class WhisperHandler:
    """仅使用 openai-whisper 的简单处理器。"""

    def __init__(self, config_or_model='base'):
        # 支持传入整个 config dict 或模型名称字符串
        if isinstance(config_or_model, dict):
            self.config = config_or_model
        else:
            self.config = {'WHISPER_MODEL': config_or_model}

        self.emergency_keywords = self._load_keywords()

        if whisper is None:
            raise RuntimeError('未检测到 whisper 库，请安装: pip install openai-whisper')

        model_name = self.config.get('WHISPER_MODEL', 'base')
        print(f'正在加载原生 Whisper 模型: {model_name}...')
        try:
            self.model = whisper.load_model(model_name)
            print('✅ 模型加载完成')
        except Exception as e:
            raise RuntimeError(f'Whisper 初始化失败: {e}')

    def _load_keywords(self):
        return [
            'help',
            '救命',
            '救',
        ]

    def transcribe(self, audio_path):
        """识别音频文件，返回 {'text': str, 'confidence': float}。"""
        try:
            result = self.model.transcribe(audio_path)
            text = result.get('text', '').strip()

            confidence = 0.0
            if result.get('segments') and len(result['segments']) > 0:
                avg_logprob = sum(seg.get('avg_logprob', -1) for seg in result['segments']) / len(result['segments'])
                confidence = max(0.0, min(1.0, (avg_logprob + 1) / 2))
            if confidence == 0.0:
                confidence = 0.85

            return {'text': text, 'confidence': round(confidence, 2)}
        except Exception as e:
            print(f'识别失败 (whisper): {e}')
            raise

    def detect_emergency(self, text):
        if not text:
            return False
        tl = text.lower()
        for k in self.emergency_keywords:
            if k.lower() in tl:
                return True
        return False
