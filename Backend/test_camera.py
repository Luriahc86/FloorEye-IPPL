import cv2
import sys
from ultralytics import YOLO

from computer_vision.detector import detect_dirty_floor

def test_camera(camera_id=0, confidence=0.5):
    """
    Test computer vision dengan live camera feed.
    
    Args:
        camera_id: ID kamera (default 0 untuk built-in webcam)
        confidence: Confidence threshold untuk deteksi (default 0.5)
    
    Kontrol:
        - 'q': Keluar
        - 'c': Capture screenshot ke test_capture.jpg
        - 'd': Toggle debug mode
    """
    
    print(f"[INFO] Membuka kamera {camera_id}...")
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        print(f"[ERROR] Gagal membuka kamera {camera_id}")
        return
    
    # Set kamera resolution dan fps
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"[INFO] Kamera resolution: {width}x{height} @ {fps} FPS")
    print("[INFO] Tekan 'q' untuk keluar, 'c' untuk capture, 'd' untuk toggle debug")
    
    debug = False
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("[ERROR] Gagal membaca frame")
                break
            
            frame_count += 1
            
            # Flip frame horizontally untuk lebih natural (seperti mirror)
            frame = cv2.flip(frame, 1)
            
            # Run deteksi
            detected = detect_dirty_floor(frame, conf_threshold=confidence, debug=debug)
            
            # Buat display frame dengan info
            display_frame = frame.copy()
            
            # Text info
            status = "🟢 LANTAI BERSIH!" if detected else "🔴 LANTAI KOTOR"
            color = (0, 255, 0) if detected else (0, 0, 255)  # BGR
            
            cv2.putText(display_frame, status, (20, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 2)
            cv2.putText(display_frame, f"Frame: {frame_count} | Conf: {confidence}", 
                       (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(display_frame, "Press 'q' to quit, 'c' to capture, 'd' for debug", 
                       (20, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            
            # Tampilkan
            cv2.imshow("FloorEye Camera Test", display_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n[INFO] Keluar...")
                break
            elif key == ord('c'):
                filename = f"test_capture_{frame_count}.jpg"
                cv2.imwrite(filename, frame)
                print(f"[INFO] Capture tersimpan: {filename}")
            elif key == ord('d'):
                debug = not debug
                print(f"[INFO] Debug mode: {'ON' if debug else 'OFF'}")
    
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[INFO] Kamera ditutup")

if __name__ == "__main__":
    camera_id = 0
    confidence = 0.5
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        try:
            camera_id = int(sys.argv[1])
        except ValueError:
            print(f"[ERROR] Invalid camera ID: {sys.argv[1]}")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        try:
            confidence = float(sys.argv[2])
        except ValueError:
            print(f"[ERROR] Invalid confidence: {sys.argv[2]}")
            sys.exit(1)
    
    test_camera(camera_id, confidence)
