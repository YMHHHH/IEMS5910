# 端侧设备模拟器 / Device Simulator

本 README 汇总 `device` 目录下所有文档的内容（虚拟环境、安装、手动下载、修复 PyAudio、启动与故障排查）

---

### 简介

端侧设备模拟器使用 Whisper 进行离线语音识别，并通过 Socket.IO 将识别事件实时发送到后端服务器。支持使用真实麦克风或模拟音频文件进行测试。

### 功能特点

- 离线语音识别（Whisper）
- 呼救关键词检测（例如："help", "救命"）
- 实时事件推送（Socket.IO）
- 支持麦克风与模拟音频两种模式

### 环境与依赖

- 推荐 Python 3.6-3.12
- 必要系统库：`ffmpeg`、`portaudio`（用于 PyAudio）、`rknn-toolkit2`

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

安装rknn-toolkit2
https://github.com/airockchip/rknn-toolkit2

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

### 获得rknn模型

1.下载预训练onnx模型
```bash
chmod +x ./model/download_onnx.sh
./model/dowmload_onnx.sh
```

2.转换rknn模型
```bash
python ./model/convert.py ./model/whisper_encoder_base_20s.onnx rk3566
# output model will be saved as ./model/whisper_encoder_base_20s.rknn

python ./model/convert.py ./model/whisper_decoder_base_20s.onnx rk3566
# output model will be saved as ./model/whisper_decoder_base_20s.rknn
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

source .env

### 运行（启动）

```bash
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
source .env
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


