
# 人脸跟踪云台控制系统

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.6%2B-green.svg)
![OpenCV](https://img.shields.io/badge/opencv-4.0%2B-orange.svg)

基于ESP32与OpenCV DNN的二轴云台人脸跟踪系统，实现实时人脸检测与自动跟踪。

## 📋 目录

- [功能特性](#功能特性)
- [硬件需求](#硬件需求)
- [软件依赖](#软件依赖)
- [快速开始](#快速开始)
- [使用说明](#使用说明)
- [项目结构](#项目结构)
- [通信协议](#通信协议)
- [PID控制参数](#pid控制参数)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## ✨ 功能特性

- 🎯 **实时人脸检测**：基于OpenCV DNN的高精度人脸检测
- 🔄 **PID控制跟踪**：采用PID算法实现平滑的人脸跟踪
- 📡 **串口通信**：PC与ESP32之间的稳定通信
- 🎮 **手动控制**：支持键盘手动控制云台方向
- 📊 **状态显示**：实时显示跟踪状态和统计信息
- 🔁 **自动扫描**：支持水平和垂直方向的自动扫描
- 💾 **帧保存**：支持随时保存当前帧为图片

## 🛠️ 硬件需求

| 组件 | 型号 | 数量 | 说明 |
|------|------|------|------|
| 主控板 | ESP32 DevKit | 1 | 核心控制单元 |
| 水平舵机 | MG996R | 1 | 控制水平旋转 |
| 垂直舵机 | MG996R | 1 | 控制垂直旋转 |
| 摄像头 | USB摄像头 | 1 | 人脸采集 |
| 电源模块 | 5V 2A | 1 | 为舵机供电 |

### 接线说明

```
ESP32          舵机
────────────────────────
GPIO 2   ────── Pan舵机信号引脚
GPIO 4   ────── Tilt舵机信号引脚
5V       ────── 舵机电源正极
GND      ────── 舵机电源负极
```

> ⚠️ **注意**：舵机必须使用5V电源，建议使用外部电源供电以避免电流不足。

## 📦 软件依赖

### PC端（Python）

```bash
pip install opencv-python numpy pyserial
```

### ESP32端

- Arduino IDE
- ESP32Servo 库（在Arduino IDE中搜索安装）

## 🚀 快速开始

### 1. 上传ESP32代码

1. 使用Arduino IDE打开 `gimbal_esp32/gimbal_esp32.ino`
2. 选择正确的开发板和端口
3. 上传代码到ESP32

### 2. 运行人脸跟踪程序

```bash
python face_tracking_gimbal.py
```

按照提示输入摄像头索引和串口号即可开始跟踪。

### 3. 手动控制云台（可选）

```bash
python gimbal.py
```

使用键盘手动控制云台的移动。

## 📖 使用说明

### 人脸跟踪模式（face_tracking_gimbal.py）

| 按键 | 功能 |
|------|------|
| `t` | 开启/关闭跟踪功能 |
| `r` | 重置云台到中心位置(90°, 90°) |
| `s` | 保存当前帧为图片 |
| `q` | 退出程序 |

### 手动控制模式（gimbal.py）

| 按键 | 功能 |
|------|------|
| `1` | 左转10度 |
| `2` | 右转10度 |
| `3` | 上转10度 |
| `4` | 下转10度 |
| `r` | 重置到中心 |
| `h` | 水平扫描(0°→180°→0°) |
| `v` | 垂直扫描(0°→180°→0°) |
| `q` | 退出 |

## 📁 项目结构

```
.
├── face_tracking_gimbal.py  # 人脸跟踪主程序
├── gimbal.py               # 云台控制模块
├── gimbal_esp32/           # ESP32代码目录
│   └── gimbal_esp32.ino    # ESP32舵机控制代码
├── face_models/            # DNN模型目录（自动创建）
│   ├── deploy.prototxt     # 网络结构定义
│   └── res10_300x300_ssd_iter_140000_fp16.caffemodel  # 预训练模型
└── README.md               # 项目说明文档
```

## 🔌 通信协议

PC通过串口向ESP32发送命令，波特率为115200。

### 命令格式

```
[命令类型][角度值]\n
```

### 命令类型

| 命令 | 说明 | 示例 |
|------|------|------|
| `P` | 设置水平角度 | `P90\n` → 设置水平角度为90° |
| `T` | 设置垂直角度 | `T45\n` → 设置垂直角度为45° |
| `R` | 重置到中心 | `R\n` → 重置到(90°, 90°) |

## 🎛️ PID控制参数

| 参数 | 水平轴 | 垂直轴 | 作用 |
|------|--------|--------|------|
| Kp (比例) | 0.1 | 0.1 | 响应速度 |
| Ki (积分) | 0.02 | 0.03 | 消除稳态误差 |
| Kd (微分) | 0.3 | 0.4 | 抑制振荡 |
| 积分限幅 | ±50 | ±50 | 防止积分饱和 |

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 🙏 致谢

- [OpenCV](https://opencv.org/) - 计算机视觉库
- [ESP32Servo](https://github.com/madhephaestus/ESP32Servo) - ESP32舵机控制库

---

**如果这个项目对您有帮助，请给个Star ⭐！**
