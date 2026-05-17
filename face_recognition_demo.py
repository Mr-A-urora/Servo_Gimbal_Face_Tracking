import cv2

def main():
    print("=== Face Detection System ===")
    print("Initializing...")
    
    # Load face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Open camera (try external first, then internal)
    print("Opening camera...")
    
    # Try external camera (index 1)
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("External camera not found, trying internal camera...")
        cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Cannot open camera!")
        return
    
    # Set camera resolution and FPS
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("Camera opened successfully")
    print("\nInstructions:")
    print("  q - Quit")
    print("  s - Save frame")
    
    # Initialize variables for motion tracking
    prev_frame = None
    frame_count = 0
    
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Cannot read frame")
            break

        frame = cv2.rotate(frame, cv2.ROTATE_180)

        frame_count += 1

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply slight blur to reduce noise (helps with motion)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Detect faces with optimized parameters for motion
        # Using more sensitive settings for moving faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,        # More sensitive (smaller value)
            minNeighbors=3,         # More sensitive (smaller value)
            minSize=(30, 30)        # Detect smaller faces
        )
        
        # Track detected faces
        for (x, y, w, h) in faces:
            # Filter by aspect ratio
            aspect_ratio = w / h
            if 0.6 < aspect_ratio < 1.5:
                # Draw rectangle and center point
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                center_x = x + w // 2
                center_y = y + h // 2
                cv2.circle(frame, (center_x, center_y), 5, (0, 255, 0), -1)
        
        # Display information
        cv2.putText(frame, f"Faces: {len(faces)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Press 's' to save, 'q' to quit", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Show frame
        cv2.imshow('Face Detection', frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            import time
            filename = f"frame_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Saved: {filename}")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("Program ended")

if __name__ == '__main__':
    main()