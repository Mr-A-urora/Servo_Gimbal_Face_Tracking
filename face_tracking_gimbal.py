"""
人脸跟踪云台控制系统
结合DNN人脸识别和二轴云台控制
"""

import cv2
import numpy as np
import time
from gimbal import GimbalController

class FaceTrackingGimbal:
    def __init__(self, camera_idx=1, serial_port='COM7'):
        """
        初始化人脸跟踪云台

        Args:
            camera_idx: 摄像头索引
            serial_port: ESP32串口号
        """
        self.gimbal = GimbalController(port=serial_port)
        self.gimbal_connected = self.gimbal.connect()

        self.cap = cv2.VideoCapture(camera_idx)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.net = self.init_dnn_model()

        self.tracking_enabled = True
        self.smooth_factor = 0.5
        self.pan_target = 90
        self.tilt_target = 90
        self.pan_current = 90
        self.tilt_current = 90

        self.pan_error_sum = 0
        self.pan_error_prev = 0
        self.tilt_error_sum = 0
        self.tilt_error_prev = 0

        self.pan_kp = 0.1
        self.pan_ki = 0.02
        self.pan_kd = 0.3

        self.tilt_kp = 0.1
        self.tilt_ki = 0.03
        self.tilt_kd = 0.4

        self.integral_limit = 50

        self.frame_count = 0
        self.face_detected_count = 0

    def init_dnn_model(self):
        """初始化DNN人脸检测模型"""
        import urllib.request
        import os

        model_dir = "face_models"
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

        prototxt_url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
        model_url = "https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20180205_fp16/res10_300x300_ssd_iter_140000_fp16.caffemodel"

        prototxt_path = os.path.join(model_dir, "deploy.prototxt")
        model_path = os.path.join(model_dir, "res10_300x300_ssd_iter_140000_fp16.caffemodel")

        if not os.path.exists(prototxt_path):
            print("Downloading deploy.prototxt...")
            urllib.request.urlretrieve(prototxt_url, prototxt_path)

        if not os.path.exists(model_path):
            print("Downloading face detection model...")
            urllib.request.urlretrieve(model_url, model_path)

        print("Loading DNN face detection model...")
        net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
        print("DNN model loaded successfully")
        return net

    def detect_faces_dnn(self, frame):
        """使用DNN检测人脸"""
        height, width = frame.shape[:2]

        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                     (300, 300), (104.0, 177.0, 123.0))
        self.net.setInput(blob)
        detections = self.net.forward()

        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                (x1, y1, x2, y2) = box.astype("int")
                faces.append((x1, y1, x2, y2, confidence))

        return faces

    def track_face(self, center_x, center_y, frame_width, frame_height):
        """根据人脸位置调整云台（使用PID控制）"""
        offset_x = center_x - frame_width / 2
        offset_y = center_y - frame_height / 2

        offset_ratio_x = offset_x / (frame_width / 2)
        offset_ratio_y = offset_y / (frame_height / 2)

        if abs(offset_ratio_x) < 0.03 and abs(offset_ratio_y) < 0.03:
            self.pan_error_sum = 0
            self.tilt_error_sum = 0
            return

        target_adjust_x = offset_ratio_x * 45
        target_adjust_y = offset_ratio_y * 45

        self.pan_target = 90 - target_adjust_x
        self.pan_target = max(0, min(180, self.pan_target))

        self.tilt_target = 90 + target_adjust_y
        self.tilt_target = max(0, min(180, self.tilt_target))

        pan_error = self.pan_target - self.pan_current
        tilt_error = self.tilt_target - self.tilt_current

        self.pan_error_sum += pan_error
        self.tilt_error_sum += tilt_error

        self.pan_error_sum = max(-self.integral_limit, min(self.integral_limit, self.pan_error_sum))
        self.tilt_error_sum = max(-self.integral_limit, min(self.integral_limit, self.tilt_error_sum))

        pan_derivative = pan_error - self.pan_error_prev
        tilt_derivative = tilt_error - self.tilt_error_prev

        self.pan_error_prev = pan_error
        self.tilt_error_prev = tilt_error

        pan_delta = self.pan_kp * pan_error + self.pan_ki * self.pan_error_sum + self.pan_kd * pan_derivative
        tilt_delta = self.tilt_kp * tilt_error + self.tilt_ki * self.tilt_error_sum + self.tilt_kd * tilt_derivative

        self.pan_current += pan_delta
        self.tilt_current += tilt_delta

        self.pan_current = max(0, min(180, self.pan_current))
        self.tilt_current = max(0, min(180, self.tilt_current))

        if self.gimbal_connected:
            self.gimbal.set_both(int(self.pan_current), int(self.tilt_current))

    def process_frame(self, frame):
        """处理单帧图像"""
        frame = cv2.rotate(frame, cv2.ROTATE_180)

        faces = self.detect_faces_dnn(frame)

        for (x1, y1, x2, y2, confidence) in faces:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            cv2.circle(frame, (center_x, center_y), 5, (0, 255, 0), -1)

            frame_center_x = frame.shape[1] // 2
            frame_center_y = frame.shape[0] // 2
            cv2.line(frame, (center_x, center_y), (frame_center_x, frame_center_y), (255, 0, 0), 1)

            cv2.putText(frame, f"Face {confidence:.2f}", (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            if self.tracking_enabled and self.gimbal_connected:
                self.track_face(center_x, center_y, frame.shape[1], frame.shape[0])

            self.face_detected_count += 1

        frame_center_x = frame.shape[1] // 2
        frame_center_y = frame.shape[0] // 2
        cv2.line(frame, (frame_center_x - 20, frame_center_y), (frame_center_x + 20, frame_center_y), (0, 255, 255), 1)
        cv2.line(frame, (frame_center_x, frame_center_y - 20), (frame_center_x, frame_center_y + 20), (0, 255, 255), 1)

        self.frame_count += 1

        status_text = f"Tracking: {'ON' if self.tracking_enabled else 'OFF'}"
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        face_text = f"Faces: {len(faces)}"
        cv2.putText(frame, face_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if self.gimbal_connected:
            angle_text = f"Pan: {int(self.pan_current)} Tilt: {int(self.tilt_current)}"
            cv2.putText(frame, angle_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        stats_text = f"Frames: {self.frame_count} Detected: {self.face_detected_count}"
        cv2.putText(frame, stats_text, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        return frame

    def run(self):
        """运行主循环"""
        if not self.cap.isOpened():
            print("无法打开摄像头!")
            return

        print("\n=== 人脸跟踪云台系统 ===")
        print("\n操作说明:")
        print("  t - 开启/关闭跟踪")
        print("  r - 重置云台到中心")
        print("  s - 保存当前帧")
        print("  q - 退出")
        print()

        if self.gimbal_connected:
            self.gimbal.reset()
            time.sleep(1)

        while True:
            ret, frame = self.cap.read()

            if not ret:
                print("无法读取帧!")
                break

            frame = self.process_frame(frame)

            cv2.imshow('Face Tracking Gimbal', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('t'):
                self.tracking_enabled = not self.tracking_enabled
                print(f"跟踪: {'开启' if self.tracking_enabled else '关闭'}")
            elif key == ord('r'):
                if self.gimbal_connected:
                    self.gimbal.reset()
                    self.pan_current = 90
                    self.tilt_current = 90
                    self.pan_target = 90
                    self.tilt_target = 90
                    print("云台已重置")
            elif key == ord('s'):
                filename = f"frame_{int(time.time())}.jpg"
                cv2.imwrite(filename, frame)
                print(f"已保存: {filename}")

    def cleanup(self):
        """清理资源"""
        if self.gimbal_connected:
            self.gimbal.reset()
            self.gimbal.disconnect()

        if self.cap.isOpened():
            self.cap.release()

        cv2.destroyAllWindows()

        print(f"\n=== 统计信息 ===")
        print(f"总帧数: {self.frame_count}")
        print(f"检测到人脸: {self.face_detected_count}")
        if self.frame_count > 0:
            print(f"检测率: {self.face_detected_count/self.frame_count*100:.1f}%")
        print("程序结束")

def main():
    print("=== DNN Face Tracking Gimbal System ===")
    print()

    print("请输入摄像头索引:")
    print("  0 - 内置摄像头")
    print("  1 - 外接摄像头")
    camera_idx = int(input("摄像头索引 (默认1): ").strip() or "1")

    print("\n请输入ESP32串口号:")
    print("  Windows: COM3, COM4, ...")
    serial_port = input("串口号 (默认COM7): ").strip() or "COM7"

    if serial_port.isdigit():
        serial_port = "COM" + serial_port

    tracker = FaceTrackingGimbal(camera_idx=camera_idx, serial_port=serial_port)

    try:
        tracker.run()
    except KeyboardInterrupt:
        print("\n程序被中断")
    finally:
        tracker.cleanup()

if __name__ == '__main__':
    main()