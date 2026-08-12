import cv2
import face_recognition
import pickle
import os
import numpy as np
from src.logger import get_logger

class FaceRecognizer:
    """
    Face recognition module optimized for low-end hardware
    """
    
    def __init__(self, encodings_path, tolerance=0.6, model="hog", upsample=0):
        self.encodings_path = encodings_path
        self.tolerance = tolerance
        self.model = model
        self.upsample = upsample
        self.known_encodings = []
        self.known_names = []
        self.logger = get_logger()
        
        self._load_encodings()
    
    def _load_encodings(self):
        """
        Load face encodings from pickle file
        """
        try:
            if not os.path.exists(self.encodings_path):
                self.logger.error(f"Encodings file not found: {self.encodings_path}")
                raise FileNotFoundError(
                    f"Face encodings not found. Please run build_embeddings.py first."
                )
            
            with open(self.encodings_path, 'rb') as f:
                data = pickle.load(f)
            
            self.known_encodings = data.get('encodings', [])
            self.known_names = data.get('names', [])
            
            if not self.known_encodings or not self.known_names:
                self.logger.error("No face encodings found in pickle file")
                raise ValueError("Empty encodings file")
            
            self.logger.info(f"Loaded {len(self.known_names)} face encodings")
            
        except Exception as e:
            self.logger.error(f"Failed to load encodings: {str(e)}")
            raise
    
    def recognize_face(self, frame):
        """
        Detect and recognize face in frame
        Returns: (name, confidence, face_location) or (None, None, None)
        """
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_recognition.face_locations(
                rgb_frame, 
                number_of_times_to_upsample=self.upsample,
                model=self.model
            )
            
            if not face_locations:
                return None, None, None
            
            # Use only the first detected face
            face_location = face_locations[0]
            
            # Encode the detected face
            face_encodings = face_recognition.face_encodings(
                rgb_frame, 
                [face_location]
            )
            
            if not face_encodings:
                return None, None, None
            
            face_encoding = face_encodings[0]
            
            # Compare with known faces
            distances = face_recognition.face_distance(self.known_encodings, face_encoding)
            
            if len(distances) == 0:
                return "Unknown", 0.0, face_location
            
            # Find best match
            min_distance = np.min(distances)
            
            if min_distance <= self.tolerance:
                best_match_idx = np.argmin(distances)
                name = self.known_names[best_match_idx]
                confidence = 1.0 - min_distance
                
                return name, confidence, face_location
            else:
                return "Unknown", 0.0, face_location
            
        except Exception as e:
            self.logger.error(f"Recognition error: {str(e)}")
            return None, None, None
    
    def draw_face_box(self, frame, face_location, name, confidence):
        """
        Draw rectangle and label on detected face
        """
        if face_location is None:
            return frame
        
        top, right, bottom, left = face_location
        
        # Choose color based on recognition
        if name == "Unknown":
            color = (0, 0, 255)  # Red
        else:
            color = (0, 255, 0)  # Green
        
        # Draw rectangle
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        
        # Draw label background
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        
        # Draw text
        label = f"{name}"
        if confidence > 0:
            label += f" ({confidence:.1%})"
        
        cv2.putText(
            frame, 
            label, 
            (left + 6, bottom - 6), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.6, 
            (255, 255, 255), 
            2
        )
        
        return frame
