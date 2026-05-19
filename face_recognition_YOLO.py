import cv2
import numpy as np
import time

def download_face_model():
    """Download face detection model if not exists"""
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
        print(f"Downloading deploy.prototxt...")
        urllib.request.urlretrieve(prototxt_url, prototxt_path)
    
    if not os.path.exists(model_path):
        print(f"Downloading face detection model... (this may take a minute)")
        urllib.request.urlretrieve(model_url, model_path)
    
    return prototxt_path, model_path

def init_camera():
    """Initialize camera - force external camera (index 1)"""
    print("Opening external camera (索引1)...")
    
    # Force external camera (index 1)
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        for _ in range(5):
            ret, frame = cap.read()
            if ret and frame is not None:
                print("成功使用外接摄像头 (索引1)")
                return cap
        
        cap.release()
    
    print("外接摄像头不可用，尝试内置摄像头...")
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        for _ in range(5):
            ret, frame = cap.read()
            if ret and frame is not None:
                print("成功使用内置摄像头 (索引0)")
                return cap
        
        cap.release()
    
    print("无法打开摄像头!")
    return None

def main():
    print("=== Advanced Face Detection System ===")
    print("Initializing...")
    
    # Download face detection model
    prototxt_path, model_path = download_face_model()
    
    # Load face detection model
    print("Loading face detection model...")
    net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
    print("Model loaded successfully")
    
    # Initialize camera
    cap = init_camera()
    if cap is None:
        print("请检查摄像头连接!")
        return
    
    print("\n操作说明:")
    print("  q - 退出")
    print("  s - 保存当前帧")
    
    while True:
        ret, frame = cap.read()

        if not ret or frame is None:
            print("无法读取帧, 尝试重新连接...")
            cap.release()
            cap = init_camera()
            if cap is None:
                break
            continue

        frame = cv2.rotate(frame, cv2.ROTATE_180)

        height, width = frame.shape[:2]
        
        # Prepare frame for face detection
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                     (300, 300), (104.0, 177.0, 123.0))
        net.setInput(blob)
        detections = net.forward()
        
        face_count = 0
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            if confidence > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                (x1, y1, x2, y2) = box.astype("int")
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                cv2.circle(frame, (center_x, center_y), 5, (0, 255, 0), -1)
                
                cv2.putText(frame, f"Face {confidence:.2f}", (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                
                face_count += 1
        
        cv2.putText(frame, f"Faces: {face_count}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Press 's' to save, 'q' to quit", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow('Advanced Face Detection', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = f"frame_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Saved: {filename}")
    
    cap.release()
    cv2.destroyAllWindows()
    print("\n程序结束")

if __name__ == '__main__':
    main()