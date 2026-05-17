# 二轴云台控制系统使用说明

## 硬件连接

### ESP32与SG90舵机连接
```
ESP32              SG90舵机
----              ------
3.3V/5V    ->   VCC (红色)
GND          ->   GND (棕色/黑色)
GPIO 2       ->   Pan舵机信号线 (橙色)  - 水平旋转
GPIO 4       ->   Tilt舵机信号线 (橙色) - 垂直旋转
```

### ESP32与电脑连接
```
ESP32              电脑
----              ------
USB线       ->   USB端口
```

## 软件安装

### 1. 安装Python依赖
```bash
pip install pyserial
```

### 2. 上传ESP32代码
1. 打开Arduino IDE
2. 安装ESP32开发板支持
3. 打开 `gimbal_esp32.ino` 文件
4. 选择正确的开发板和端口
5. 上传代码到ESP32

## 使用方法

### 方法1: Python控制台控制
```bash
python gimbal.py
```

**操作命令:**
- `1` - 左转10度
- `2` - 右转10度
- `3` - 上转10度
- `4` - 下转10度
- `r` - 重置到中心位置 (90, 90)
- `h` - 水平扫描
- `v` - 垂直扫描
- `q` - 退出程序

### 方法2: Web浏览器控制
1. 上传ESP32代码后，ESP32会创建WiFi热点
2. 连接到ESP32的WiFi
3. 在浏览器中访问 `http://192.168.4.1`
4. 使用滑块控制云台

### 方法3: Python程序控制
```python
from gimbal import GimbalController

# 创建控制器
gimbal = GimbalController(port='COM3')  # 根据实际情况修改串口号

# 连接
gimbal.connect()

# 控制云台
gimbal.set_pan(90)      # 设置水平角度
gimbal.set_tilt(90)     # 设置垂直角度
gimbal.set_both(90, 90) # 同时设置两个角度
gimbal.reset()          # 重置到中心

# 扫描
gimbal.scan_horizontal()  # 水平扫描
gimbal.scan_vertical()   # 垂直扫描

# 断开连接
gimbal.disconnect()
```

## 与人脸识别结合

### 示例代码
```python
import cv2
from gimbal import GimbalController

# 初始化云台
gimbal = GimbalController(port='COM3')
gimbal.connect()

# 初始化人脸检测
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 打开摄像头
cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    
    # 检测人脸
    faces = face_cascade.detectMultiScale(frame, 1.1, 4)
    
    for (x, y, w, h) in faces:
        # 绘制人脸框
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        
        # 计算中心点
        center_x = x + w // 2
        center_y = y + h // 2
        
        # 云台跟踪
        gimbal.track_face(center_x, center_y, frame.shape[1], frame.shape[0])
    
    cv2.imshow('Face Tracking', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 清理
cap.release()
cv2.destroyAllWindows()
gimbal.disconnect()
```

## 故障排除

### 串口连接失败
1. 检查ESP32是否正确连接到电脑
2. 在设备管理器中查看ESP32的串口号
3. 确保没有其他程序占用该串口
4. 尝试更换USB线或USB端口

### 舵机不动作
1. 检查舵机电源是否充足（建议使用外部5V电源）
2. 检查信号线连接是否正确
3. 确认ESP32代码已正确上传

### 云台抖动
1. 检查电源稳定性
2. 减小角度调整步进值
3. 检查机械结构是否松动

## 注意事项

1. **电源**: SG90舵机需要5V电源，ESP32的3.3V可能不足以驱动两个舵机
2. **角度限制**: 舵机角度范围0-180度，超出范围可能损坏舵机
3. **机械限制**: 云台机械结构可能有物理限制，需要调整代码中的角度范围
4. **安全**: 舵机旋转时注意不要夹手

## 技术参数

- **舵机型号**: SG90
- **工作电压**: 4.8V - 6V
- **角度范围**: 0° - 180°
- **控制信号**: PWM (50Hz)
- **通信**: UART (115200 baud)
- **响应速度**: 约0.1秒/60度