import cv2
import time
from datetime import datetime
from src.camera import Camera
from src.face_recognition_module import FaceRecognizer
from src.database import AttendanceDatabase
from src.logger import get_logger


class AttendanceManager:
    """
    Manage attendance recognition session
    """

    def __init__(self, config):
        self.config = config
        self.logger = get_logger()

        # Initialize recognizer and database once
        self.recognizer = FaceRecognizer(
            encodings_path=config.ENCODINGS_PATH,
            tolerance=config.RECOGNITION_TOLERANCE,
            model=config.RECOGNITION_MODEL,
            upsample=config.FACE_DETECTION_UPSAMPLE
        )

        self.database = AttendanceDatabase(config.DATABASE_PATH)

        # Camera will be created per session
        self.camera = None

        # Session state
        self.frame_counter = 0
        self.check_type = None
        self.recognized_employee = None

    def start_session(self, check_type):
        """
        Start attendance recognition session
        Returns: (success, employee_name, confidence, error_message)
        """
        # Reset session state
        self.check_type = check_type
        self.recognized_employee = None
        self.frame_counter = 0

        self.logger.info(f"Starting {check_type} session")

        # Create fresh camera instance for this session
        self.camera = Camera(
            camera_id=self.config.CAMERA_ID,
            width=self.config.CAMERA_WIDTH,
            height=self.config.CAMERA_HEIGHT,
            fallback_width=self.config.FALLBACK_WIDTH,
            fallback_height=self.config.FALLBACK_HEIGHT
        )

        # Open camera
        if not self.camera.open():
            error_msg = "Cannot open camera. Please check camera connection."
            self.logger.error(error_msg)
            self.camera = None
            return False, None, None, error_msg

        timeout = self.config.RECOGNITION_TIMEOUT
        window_name = f"{self.config.ORGANIZATION_NAME} - {check_type}"

        # Create window
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        # ── Startup delay (2 seconds countdown before recognition begins) ──
        STARTUP_DELAY = 2.0
        delay_start = time.time()

        while True:
            elapsed_delay = time.time() - delay_start
            remaining_delay = STARTUP_DELAY - elapsed_delay

            if remaining_delay <= 0:
                break

            ret, frame = self.camera.read()
            if not ret:
                self._cleanup_session(window_name)
                return False, None, None, "Failed to read from camera"

            # Countdown overlay
            cv2.putText(
                frame,
                f"Starting in {remaining_delay:.1f}s...",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 165, 255),  # Orange
                2
            )
            cv2.putText(
                frame,
                "Please face the camera",
                (10, frame.shape[0] - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
            cv2.putText(
                frame,
                "Press 'q' to cancel",
                (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.imshow(window_name, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                self._cleanup_session(window_name)
                self.logger.info("Session cancelled by user during countdown")
                return False, None, None, "Cancelled by user"
        # ── End of startup delay ──

        # Recognition loop — timeout starts AFTER delay
        start_time = time.time()

        try:
            while True:
                # Check timeout
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    self._cleanup_session(window_name)
                    error_msg = f"Timeout: No face recognized in {timeout} seconds"
                    self.logger.warning(error_msg)
                    return False, None, None, error_msg

                # Read frame
                ret, frame = self.camera.read()

                if not ret:
                    self._cleanup_session(window_name)
                    error_msg = "Failed to read from camera"
                    self.logger.error(error_msg)
                    return False, None, None, error_msg

                # Process frame based on frame skip
                self.frame_counter += 1

                if self.frame_counter % self.config.FRAME_SKIP == 0:
                    # Recognize face
                    name, confidence, face_location = self.recognizer.recognize_face(
                        frame)

                    # Draw face box
                    if face_location is not None:
                        frame = self.recognizer.draw_face_box(
                            frame, face_location, name, confidence)

                    # Check if recognized
                    if name is not None and name != "Unknown":
                        self.logger.info(
                            f"Recognized: {name} (Confidence: {confidence:.2%})")

                        # Save attendance
                        employee_id = name
                        success = self.database.add_attendance(
                            employee_id=employee_id,
                            employee_name=name,
                            check_type=check_type,
                            confidence=confidence,
                            camera_id=self.config.CAMERA_ID
                        )

                        self._cleanup_session(window_name)

                        if success:
                            return True, name, confidence, None
                        else:
                            error_msg = "Failed to save attendance to database"
                            return False, name, confidence, error_msg

                    elif name == "Unknown":
                        self.logger.warning("Unknown face detected")

                # Display FPS and remaining time
                fps = self.camera.get_fps()
                remaining_time = int(timeout - elapsed_time)

                cv2.putText(
                    frame,
                    f"FPS: {fps:.1f} | Time: {remaining_time}s",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    "Stand 50-120 cm from camera",
                    (10, frame.shape[0] - 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    "Press 'q' to cancel",
                    (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

                # Show frame
                cv2.imshow(window_name, frame)

                # Check for quit
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:
                    self._cleanup_session(window_name)
                    self.logger.info("Session cancelled by user")
                    return False, None, None, "Cancelled by user"

        except Exception as e:
            self._cleanup_session(window_name)
            error_msg = f"Recognition error: {str(e)}"
            self.logger.error(error_msg)
            return False, None, None, error_msg

    def _cleanup_session(self, window_name):
        """
        Clean up resources after a session
        """
        if self.camera is not None:
            self.camera.release()
            self.camera = None

        try:
            cv2.destroyWindow(window_name)
        except:
            pass

        cv2.destroyAllWindows()
        cv2.waitKey(1)

    def cleanup(self):
        """
        Cleanup resources on application exit
        """
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        cv2.destroyAllWindows()
        cv2.waitKey(1)
