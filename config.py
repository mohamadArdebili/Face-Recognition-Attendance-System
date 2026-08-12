import os

# Project Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "dataset")  # Dataset now inside project folder
ENCODINGS_PATH = os.path.join(BASE_DIR, "data", "faces.pkl")
DATABASE_PATH = os.path.join(BASE_DIR, "data", "attendance.db")
LOG_PATH = os.path.join(BASE_DIR, "logs", "attendance.log")

# Camera Settings
CAMERA_ID = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
FALLBACK_WIDTH = 320
FALLBACK_HEIGHT = 240

# Recognition Settings
RECOGNITION_MODEL = "hog"  # Use HOG only (lightweight)
RECOGNITION_TOLERANCE = 0.6  # Lower = stricter (0.0 - 1.0)
FACE_DETECTION_UPSAMPLE = 0  # 0 for speed on old hardware
FRAME_SKIP = 2  # Process every 2nd frame (1 = every frame, 2 = every 2nd, 3 = every 3rd)

# Timeout Settings
RECOGNITION_TIMEOUT = 15  # seconds

# UI Settings
ORGANIZATION_NAME = "Face Recognition Attendance System"
SUCCESS_DISPLAY_TIME = 2500  # milliseconds
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Database Settings
DB_TABLE_NAME = "attendance"

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
