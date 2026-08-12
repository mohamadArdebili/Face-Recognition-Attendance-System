#!/usr/bin/env python3
"""
System Check Utility
Verify system requirements and configuration
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from src.utils import check_python_version, check_dependencies, validate_dataset_structure, get_system_info

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_status(label, status, message=""):
    """Print status with label"""
    status_symbol = "[✓]" if status else "[✗]"
    print(f"{status_symbol} {label}: {message}")

def main():
    """Run system checks"""
    print_header("FACE RECOGNITION ATTENDANCE SYSTEM - SYSTEM CHECK")
    
    all_ok = True
    
    # Python Version Check
    print_header("Python Version")
    py_ok, py_version = check_python_version()
    print_status("Python Version", py_ok, py_version)
    if not py_ok:
        print("    Warning: Python 3.7-3.11 recommended for best compatibility")
    all_ok = all_ok and py_ok
    
    # Dependencies Check
    print_header("Python Dependencies")
    installed, missing = check_dependencies()
    
    if installed:
        print("\n✓ Installed packages:")
        for pkg in installed:
            print(f"  - {pkg}")
    
    if missing:
        print("\n✗ Missing packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nRun: pip install -r requirements.txt")
        all_ok = False
    else:
        print_status("All Dependencies", True, "All required packages installed")
    
    # System Info
    print_header("System Information")
    info = get_system_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Configuration Check
    print_header("Configuration")
    print(f"  Dataset Path: {config.DATASET_PATH}")
    print(f"  Encodings Path: {config.ENCODINGS_PATH}")
    print(f"  Database Path: {config.DATABASE_PATH}")
    print(f"  Log Path: {config.LOG_PATH}")
    print(f"  Camera ID: {config.CAMERA_ID}")
    print(f"  Recognition Model: {config.RECOGNITION_MODEL}")
    print(f"  Recognition Tolerance: {config.RECOGNITION_TOLERANCE}")
    print(f"  Frame Skip: {config.FRAME_SKIP}")
    
    # Dataset Check
    print_header("Dataset Validation")
    dataset_ok, dataset_msg = validate_dataset_structure(config.DATASET_PATH)
    print_status("Dataset", dataset_ok, dataset_msg)
    all_ok = all_ok and dataset_ok
    
    # Encodings Check
    print_header("Face Encodings")
    encodings_exist = os.path.exists(config.ENCODINGS_PATH)
    if encodings_exist:
        size = os.path.getsize(config.ENCODINGS_PATH)
        print_status("Encodings File", True, f"Found ({size} bytes)")
    else:
        print_status("Encodings File", False, "Not found - run build_embeddings.py")
        all_ok = False
    
    # Directory Structure
    print_header("Directory Structure")
    
    directories = {
        'Data Directory': os.path.dirname(config.DATABASE_PATH),
        'Logs Directory': os.path.dirname(config.LOG_PATH)
    }
    
    for name, path in directories.items():
        exists = os.path.exists(path)
        if not exists:
            print_status(name, False, f"Missing: {path}")
        else:
            print_status(name, True, f"Exists: {path}")
    
    # Camera Check
    print_header("Camera Check")
    try:
        import cv2
        cap = cv2.VideoCapture(config.CAMERA_ID)
        if cap.isOpened():
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print_status("Camera", True, f"Available (Resolution: {width}x{height})")
            cap.release()
        else:
            print_status("Camera", False, f"Cannot open camera {config.CAMERA_ID}")
            print("    Try different CAMERA_ID in config.py")
            all_ok = False
    except Exception as e:
        print_status("Camera", False, f"Error: {str(e)}")
        all_ok = False
    
    # Final Summary
    print_header("Summary")
    if all_ok:
        print("\n✓ ALL CHECKS PASSED!")
        print("\nYou can run the application:")
        print("  python app.py")
    else:
        print("\n✗ SOME CHECKS FAILED")
        print("\nPlease fix the issues above before running the application.")
        print("See INSTALLATION.txt for detailed installation instructions.")
    
    print("\n" + "=" * 70 + "\n")
    
    return all_ok

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nCheck cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {str(e)}")
        sys.exit(1)
