"""
Utility functions for the Face Recognition Attendance System
"""

import os
import sys
from datetime import datetime

def check_python_version():
    """
    Check if Python version is compatible
    """
    version = sys.version_info
    if version.major == 3 and version.minor >= 7 and version.minor <= 11:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"Python {version.major}.{version.minor}.{version.micro} (requires 3.7-3.11)"

def check_dependencies():
    """
    Check if all required packages are installed
    """
    required_packages = {
        'cv2': 'opencv-python',
        'face_recognition': 'face-recognition',
        'numpy': 'numpy',
        'PIL': 'Pillow',
        'tkinter': 'tkinter (built-in)'
    }
    
    missing = []
    installed = []
    
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            installed.append(pip_name)
        except ImportError:
            missing.append(pip_name)
    
    return installed, missing

def format_file_size(size_bytes):
    """
    Format file size in human-readable format
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def get_system_info():
    """
    Get basic system information
    """
    import platform
    
    info = {
        'OS': platform.system(),
        'OS Version': platform.release(),
        'Architecture': platform.machine(),
        'Python Version': platform.python_version(),
        'Hostname': platform.node()
    }
    
    return info

def validate_dataset_structure(dataset_path):
    """
    Validate dataset folder structure
    """
    if not os.path.exists(dataset_path):
        return False, f"Dataset path does not exist: {dataset_path}"
    
    if not os.path.isdir(dataset_path):
        return False, f"Dataset path is not a directory: {dataset_path}"
    
    employee_folders = [f for f in os.listdir(dataset_path) 
                       if os.path.isdir(os.path.join(dataset_path, f))]
    
    if not employee_folders:
        return False, "No employee folders found in dataset"
    
    # Check each employee folder has images
    empty_folders = []
    for folder in employee_folders:
        folder_path = os.path.join(dataset_path, folder)
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
        has_images = any(f.lower().endswith(image_extensions) 
                        for f in os.listdir(folder_path) 
                        if os.path.isfile(os.path.join(folder_path, f)))
        
        if not has_images:
            empty_folders.append(folder)
    
    if empty_folders:
        return False, f"Folders without images: {', '.join(empty_folders)}"
    
    return True, f"Valid dataset with {len(employee_folders)} employees"

def export_attendance_csv(database, output_path, start_date=None, end_date=None):
    """
    Export attendance records to CSV file
    """
    import sqlite3
    import csv
    
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        if start_date and end_date:
            query = """
                SELECT employee_id, employee_name, check_type, date, time, 
                       confidence, camera_id, timestamp
                FROM attendance
                WHERE date BETWEEN ? AND ?
                ORDER BY timestamp DESC
            """
            cursor.execute(query, (start_date, end_date))
        else:
            query = """
                SELECT employee_id, employee_name, check_type, date, time, 
                       confidence, camera_id, timestamp
                FROM attendance
                ORDER BY timestamp DESC
            """
            cursor.execute(query)
        
        rows = cursor.fetchall()
        
        if rows:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Employee ID', 'Employee Name', 'Check Type', 
                               'Date', 'Time', 'Confidence', 'Camera ID', 'Timestamp'])
                writer.writerows(rows)
            
            conn.close()
            return True, f"Exported {len(rows)} records to {output_path}"
        else:
            conn.close()
            return False, "No records found"
    
    except Exception as e:
        return False, f"Export error: {str(e)}"

def get_today_summary(database):
    """
    Get summary of today's attendance
    """
    import sqlite3
    
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        # Total check-ins
        cursor.execute("""
            SELECT COUNT(*) FROM attendance 
            WHERE date = ? AND check_type = 'CHECK IN'
        """, (today,))
        check_ins = cursor.fetchone()[0]
        
        # Total check-outs
        cursor.execute("""
            SELECT COUNT(*) FROM attendance 
            WHERE date = ? AND check_type = 'CHECK OUT'
        """, (today,))
        check_outs = cursor.fetchone()[0]
        
        # Unique employees
        cursor.execute("""
            SELECT COUNT(DISTINCT employee_name) FROM attendance 
            WHERE date = ?
        """, (today,))
        unique_employees = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'date': today,
            'check_ins': check_ins,
            'check_outs': check_outs,
            'unique_employees': unique_employees,
            'total_records': check_ins + check_outs
        }
    
    except Exception as e:
        return None
