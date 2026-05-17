import serial
import time
import sys

class GimbalController:
    def __init__(self, port='COM7', baudrate=115200):
        """
        初始化云台控制器
        
        Args:
            port: 串口号 (Windows: COMx, Linux/Mac: /dev/ttyUSBx)
            baudrate: 波特率，默认115200
        """
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.pan_angle = 90
        self.tilt_angle = 90
        
    def connect(self):
        """连接到ESP32"""
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # 等待ESP32启动
            print(f"成功连接到 {self.port}")
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            print("请检查:")
            print("1. ESP32是否已连接到电脑")
            print("2. 串口号是否正确")
            print("3. 是否有其他程序占用该串口")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("已断开连接")
    
    def send_command(self, command):
        """发送命令到ESP32"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.write(command.encode())
            self.serial_conn.flush()
        else:
            print("错误: 未连接到ESP32")
    
    def set_pan(self, angle):
        """
        设置水平角度 (0-180度)
        
        Args:
            angle: 水平角度 (0-180)
        """
        angle = max(0, min(180, angle))  # 限制在0-180度范围内
        self.pan_angle = angle
        command = f"P{angle}\n"
        self.send_command(command)
        print(f"水平角度: {angle}°")
    
    def set_tilt(self, angle):
        """
        设置垂直角度 (0-180度)
        
        Args:
            angle: 垂直角度 (0-180)
        """
        angle = max(0, min(180, angle))  # 限制在0-180度范围内
        self.tilt_angle = angle
        command = f"T{angle}\n"
        self.send_command(command)
        print(f"垂直角度: {angle}°")
    
    def set_both(self, pan_angle, tilt_angle):
        """
        同时设置水平和垂直角度
        
        Args:
            pan_angle: 水平角度 (0-180)
            tilt_angle: 垂直角度 (0-180)
        """
        self.set_pan(pan_angle)
        self.set_tilt(tilt_angle)
    
    def reset(self):
        """重置到中心位置 (90, 90)"""
        self.set_both(90, 90)
    
    def scan_horizontal(self, start=0, end=180, step=10, delay=0.1):
        """
        水平扫描
        
        Args:
            start: 起始角度
            end: 结束角度
            step: 步进角度
            delay: 每步延迟时间(秒)
        """
        print(f"开始水平扫描: {start}° -> {end}°")
        for angle in range(start, end + 1, step):
            self.set_pan(angle)
            time.sleep(delay)
        
        print(f"反向扫描: {end}° -> {start}°")
        for angle in range(end, start - 1, -step):
            self.set_pan(angle)
            time.sleep(delay)
    
    def scan_vertical(self, start=0, end=180, step=10, delay=0.1):
        """
        垂直扫描
        
        Args:
            start: 起始角度
            end: 结束角度
            step: 步进角度
            delay: 每步延迟时间(秒)
        """
        print(f"开始垂直扫描: {start}° -> {end}°")
        for angle in range(start, end + 1, step):
            self.set_tilt(angle)
            time.sleep(delay)
        
        print(f"反向扫描: {end}° -> {start}°")
        for angle in range(end, start - 1, -step):
            self.set_tilt(angle)
            time.sleep(delay)
    
    def track_face(self, center_x, center_y, frame_width, frame_height):
        """
        根据人脸中心点位置调整云台
        
        Args:
            center_x: 人脸中心X坐标
            center_y: 人脸中心Y坐标
            frame_width: 帧宽度
            frame_height: 帧高度
        """
        # 计算偏移量
        offset_x = center_x - frame_width / 2
        offset_y = center_y - frame_height / 2
        
        # 设置阈值，避免频繁调整
        threshold_x = frame_width * 0.1
        threshold_y = frame_height * 0.1
        
        # 调整水平角度
        if abs(offset_x) > threshold_x:
            pan_step = int(offset_x / frame_width * 10)
            new_pan = self.pan_angle - pan_step
            new_pan = max(0, min(180, new_pan))
            self.set_pan(new_pan)
        
        # 调整垂直角度
        if abs(offset_y) > threshold_y:
            tilt_step = int(offset_y / frame_height * 10)
            new_tilt = self.tilt_angle + tilt_step
            new_tilt = max(0, min(180, new_tilt))
            self.set_tilt(new_tilt)

def main():
    print("=== 二轴云台控制器 ===")
    print()
    
    # 创建云台控制器
    print("请输入ESP32的串口号:")
    print("  Windows: COM3, COM4, ...")
    print("  Linux/Mac: /dev/ttyUSB0, /dev/ttyUSB1, ...")
    port = input("串口号 (默认COM7): ").strip() or "COM7"
    
    # 如果用户只输入数字，自动添加COM前缀
    if port.isdigit():
        port = "COM" + port
    
    gimbal = GimbalController(port=port)
    
    # 连接到ESP32
    if not gimbal.connect():
        return
    
    print("\n操作说明:")
    print("  1 - 左转")
    print("  2 - 右转")
    print("  3 - 上转")
    print("  4 - 下转")
    print("  r - 重置到中心")
    print("  h - 水平扫描")
    print("  v - 垂直扫描")
    print("  q - 退出")
    print()
    
    try:
        # 重置到中心位置
        gimbal.reset()
        time.sleep(1)
        
        while True:
            cmd = input("请输入命令: ").strip().lower()
            
            if cmd == '1':
                gimbal.set_pan(gimbal.pan_angle - 10)
            elif cmd == '2':
                gimbal.set_pan(gimbal.pan_angle + 10)
            elif cmd == '3':
                gimbal.set_tilt(gimbal.tilt_angle - 10)
            elif cmd == '4':
                gimbal.set_tilt(gimbal.tilt_angle + 10)
            elif cmd == 'r':
                gimbal.reset()
            elif cmd == 'h':
                gimbal.scan_horizontal()
                gimbal.reset()
            elif cmd == 'v':
                gimbal.scan_vertical()
                gimbal.reset()
            elif cmd == 'q':
                print("退出程序")
                break
            else:
                print("无效命令")
    
    except KeyboardInterrupt:
        print("\n程序被中断")
    finally:
        gimbal.reset()
        gimbal.disconnect()

if __name__ == '__main__':
    main()