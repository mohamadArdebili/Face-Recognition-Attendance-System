import cv2
import time
from src.logger import get_logger

class Camera:
    """
    Camera manager optimized for old USB webcams
    """
    
    def __init__(self, camera_id=0, width=640, height=480, fallback_width=320, fallback_height=240):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.fallback_width = fallback_width
        self.fallback_height = fallback_height
        self.cap = None
        self.logger = get_logger()
        self.fps_start_time = None
        self.fps_frame_count = 0
        self.current_fps = 0
    
    def open(self):
        """
        Open camera with resolution fallback
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                self.logger.error(f"Cannot open camera {self.camera_id}")
                return False
            
            # Try preferred resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            
            # Verify resolution
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Fallback to lower resolution if needed
            if actual_width != self.width or actual_height != self.height:
                self.logger.warning(
                    f"Resolution {self.width}x{self.height} not supported, "
                    f"trying {self.fallback_width}x{self.fallback_height}"
                )
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.fallback_width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.fallback_height)
                
                actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            self.logger.info(f"Camera opened: {actual_width}x{actual_height}")
            
            # Initialize FPS counter
            self.fps_start_time = time.time()
            self.fps_frame_count = 0
            
            return True
            
        except Exception as e:
            self.logger.error(f"Camera open error: {str(e)}")
            return False
    
    def read(self):
        """
        Read frame from camera
        """
        if self.cap is None or not self.cap.isOpened():
            return False, None
        
        ret, frame = self.cap.read()
        
        if ret:
            # Update FPS
            self.fps_frame_count += 1
            elapsed_time = time.time() - self.fps_start_time
            
            if elapsed_time > 1.0:
                self.current_fps = self.fps_frame_count / elapsed_time
                self.fps_frame_count = 0
                self.fps_start_time = time.time()
        
        return ret, frame
    
    def get_fps(self):
        """
        Get current FPS
        """
        return self.current_fps
    
    def release(self):
        """
        Release camera
        """
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self.logger.info("Camera released")
    
    def is_opened(self):
        """
        Check if camera is opened
        """
        return self.cap is not None and self.cap.isOpened()
