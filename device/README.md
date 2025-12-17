# 端侧设备模拟器 / Device Simulator

本 README 汇总 `device` 目录下所有文档的内容（虚拟环境、安装、手动下载、修复 PyAudio、启动与故障排查），并提供中英双语说明。中文在前，英文在后。

---

## 中文说明

### 简介

端侧设备模拟器使用 Whisper 进行离线语音识别，并通过 Socket.IO 将识别事件实时发送到后端服务器。支持使用真实麦克风或模拟音频文件进行测试。

### 功能特点

- 离线语音识别（Whisper）
- 呼救关键词检测（例如："help", "救命"）
- 实时事件推送（Socket.IO）
- 支持麦克风与模拟音频两种模式

### 环境与依赖

- 推荐 Python 3.13（openai-whisper 在 Python 3.14 上可能有兼容性问题）
- 必要系统库：`ffmpeg`、`portaudio`（用于 PyAudio）

安装 `ffmpeg`：

macOS:
```bash
brew install ffmpeg
```

Ubuntu/Debian:
```bash
sudo apt-get install ffmpeg
```

安装系统级 PortAudio（macOS 示例）：
```bash
brew install portaudio
```

如果在 Linux（例如 Orange Pi）上：
```bash
sudo apt update
sudo apt install -y alsa-utils portaudio19-dev libasound2-dev ffmpeg python3-pyaudio
```

### 虚拟环境与 Python 版本（重要）

openai-whisper 的依赖 `numba` 可能不支持 Python 3.14，建议使用 Python 3.13。使用 `pyenv` 安装并创建虚拟环境的步骤：

```bash
# 安装 pyenv（如需要）
curl https://pyenv.run | bash
source ~/.zshrc

# 安装并设置 Python 3.13
pyenv install 3.13.2
pyenv local 3.13.2

# 重新创建虚拟环境并安装依赖
rm -rf venv
bash create-venv.sh
source venv/bin/activate
pip install -r requirements-basic.txt
```

验证示例：
```bash
python --version
pip list | grep -E "(numpy|socketio|whisper|pyaudio)"
```

### 手动下载 Whisper 模型（当自动下载失败）

如果自动下载模型遇到 SSL/403 等错误，可手动下载并放入缓存目录：

```bash
mkdir -p ~/.cache/whisper
# 下载后把模型文件放到缓存目录，文件名需为 base.pt / tiny.pt 等
mv ~/Downloads/base.pt ~/.cache/whisper/base.pt
```

示例模型链接（可能会更新，请以官方源为准）：
- base: https://openaipublic.azureedge.net/.../base.pt
- tiny: https://openaipublic.azureedge.net/.../tiny.pt

然后运行：
```bash
source venv/bin/activate
export MOCK_AUDIO=false
python device.py
```

### 修复 PyAudio 安装问题

常见错误：
```
fatal error: 'portaudio.h' file not found
```

解决方式：

macOS（推荐使用 Homebrew）：
```bash
brew install portaudio
source venv/bin/activate
pip install pyaudio
```

或手动编译 PortAudio（高级）：
```bash
# 下载并编译 portaudio 源码
./configure
make
sudo make install
pip install pyaudio
```

如果暂时不需要麦克风，可在项目中使用模拟音频模式：
```bash
export MOCK_AUDIO=true
python device.py
```

### 配置（环境变量）

```bash
export SERVER_URL=http://localhost:3001
export DEVICE_ID=elder-device-01
export WHISPER_MODEL=base      # tiny / base / small / medium / large
export MOCK_AUDIO=false       # false = use microphone, true = use audio files
export SILENCE_THRESHOLD=500
export MIN_AUDIO_DURATION=1.0
export MAX_AUDIO_DURATION=5.0
# （可选）指定 PyAudio 设备索引
export AUDIO_DEVICE_INDEX=2
```

### 运行（启动）

使用真实麦克风（推荐）：

```bash
cd device
source venv/bin/activate
export MOCK_AUDIO=false
export WHISPER_MODEL=base
python device.py
```

使用模拟音频文件：

```bash
export MOCK_AUDIO=true
# 确保 audio_samples/ 中有测试文件
python device.py
```

### Orange Pi / Linux 音频快速说明

列出 ALSA 设备：
```bash
arecord -l
```

用 PyAudio 列出索引（在虚拟环境中）：
```bash
python - <<'PY'
import pyaudio
p=pyaudio.PyAudio()
for i in range(p.get_device_count()):
		info=p.get_device_info_by_index(i)
		if info['maxInputChannels']>0:
				print(i, info['name'])
p.terminate()
PY
```

测试录音（arecord）：
```bash
arecord -D hw:1,0 -f S16_LE -r 16000 -c 1 -d 5 test.wav
aplay test.wav
```

### 完整系统运行（示例）

在三台终端分别启动：

1) 后端服务器：
```bash
cd ../server
npm install
npm start
```

2) Dashboard（前端）：
```bash
cd ../dashboard
npm install
npm run dev
```

3) 设备模拟器：
```bash
cd ../device
source venv/bin/activate
export MOCK_AUDIO=false
python device.py
```

### 停止与故障排查

- 优雅停止：在程序终端按 `Ctrl+C`。
- 快速停止所有：`./stop-all.sh`（仓库根目录）。
- 常见问题：
	- 无法连接服务器：确认后端已启动并且 `SERVER_URL` 正确。
	- PyAudio 安装失败：安装 portaudio 开发包或使用系统包管理器安装 python3-pyaudio。
	- 模型下载慢或失败：可手动下载到 `~/.cache/whisper/` 并重试。

---

## English — Consolidated Guide

This README consolidates all device-side documentation (virtualenv guide, manual model download, PyAudio fixes, start instructions) into a single bilingual file.

### Overview

The device simulator performs offline speech recognition with Whisper and sends events to the backend via Socket.IO. It supports microphone input and mock-audio modes for testing.

### Features

- Offline speech recognition (Whisper)
- Emergency keyword detection (e.g. "help", "救命")
- Real-time event delivery via Socket.IO
- Microphone and mock audio modes

### Requirements

- Recommended: Python 3.13 (openai-whisper may not be compatible with Python 3.14)
- System tools: `ffmpeg`, PortAudio (for PyAudio)

Install ffmpeg (macOS):
```bash
brew install ffmpeg
```
Ubuntu/Debian:
```bash
sudo apt-get install ffmpeg
```

Install PortAudio (macOS):
```bash
brew install portaudio
```
On Linux (e.g. Orange Pi):
```bash
sudo apt update
sudo apt install -y alsa-utils portaudio19-dev libasound2-dev ffmpeg python3-pyaudio
```

### Virtualenv & Python version

Use `pyenv` to install Python 3.13 and create a virtualenv:

```bash
curl https://pyenv.run | bash
source ~/.zshrc
pyenv install 3.13.2
pyenv local 3.13.2
rm -rf venv
bash create-venv.sh
source venv/bin/activate
pip install -r requirements-basic.txt
```

### Manual model download

If automatic download fails, manually download the model file and place it in `~/.cache/whisper/` with the correct filename (e.g. `base.pt`).

### Fix PyAudio installation

If you get `portaudio.h not found`, install PortAudio via your package manager and reinstall PyAudio:

macOS (Homebrew):
```bash
brew install portaudio
source venv/bin/activate
pip install pyaudio
```

Or build PortAudio from source and then `pip install pyaudio`.

If you only need to test functionality temporarily, run in mock audio mode:
```bash
export MOCK_AUDIO=true
python device.py
```

### Environment variables examples

```bash
export SERVER_URL=http://localhost:3001
export DEVICE_ID=elder-device-01
export WHISPER_MODEL=base
export MOCK_AUDIO=false
export AUDIO_DEVICE_INDEX=2
```

### Run the device

Microphone mode (recommended):

```bash
cd device
source venv/bin/activate
export MOCK_AUDIO=false
python device.py
```
Mock audio files:
```bash
export MOCK_AUDIO=true
python device.py
```

### Orange Pi / ALSA quick notes

List ALSA devices:
```bash
arecord -l
```
List PyAudio devices (in venv):
```bash
python - <<'PY'
import pyaudio
p=pyaudio.PyAudio()
for i in range(p.get_device_count()):
		info=p.get_device_info_by_index(i)
		if info['maxInputChannels']>0:
				print(i, info['name'])
p.terminate()
PY
```

Test recording:
```bash
arecord -D hw:1,0 -f S16_LE -r 16000 -c 1 -d 5 test.wav
aplay test.wav
```

### Run all components (example)

1) Backend:
```bash
cd ../server
npm install
npm start
```
2) Dashboard:
```bash
cd ../dashboard
npm install
npm run dev
```
3) Device:
```bash
cd ../device
source venv/bin/activate
export MOCK_AUDIO=false
python device.py
```

### Troubleshooting & Notes

- Stop gracefully with `Ctrl+C`.
- Use `./stop-all.sh` to stop all components quickly.
- If model download is slow on Orange Pi, download on a PC and copy to `~/.cache/whisper/`.
- For production, consider converting models to optimized formats (ONNX/RKNN) for NPU acceleration.

---

如果你确认我可以删除单独的 md 文件（`VENV-GUIDE.md`、`MANUAL-DOWNLOAD.md`、`START.md`、`FIX-PYAUDIO.md`），我会在下一步删除它们。


