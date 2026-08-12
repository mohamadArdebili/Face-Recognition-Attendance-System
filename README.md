# Face Recognition Attendance System

A lightweight, production-ready face recognition attendance system optimized for low-end hardware (Windows 7, 2GB RAM, old CPU, no GPU).

## Features

- **Lightweight**: Optimized for old hardware using HOG detection only
- **User-friendly**: Simple Tkinter GUI with CHECK IN/OUT buttons
- **Automatic**: Recognizes employees and saves attendance automatically
- **Database**: SQLite database for attendance records
- **Logging**: Comprehensive logging system
- **Configurable**: Easy configuration without code changes
- **Portable**: Complete self-contained project with dataset included
- **Extensible**: Add new employees without modifying code

## System Requirements

- Windows 7 or higher
- 2GB RAM minimum
- Python 3.7 - 3.9 (Python 3.10+ may have dlib compatibility issues)
- USB Webcam
- Internet connection (for initial installation only)

## Project Structure

```
FaceAttendanceSystem/
├── app.py                          # Main application
├── build_embeddings.py              # Build face encodings
├── config.py                        # Configuration file
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── src/                            # Source modules
│   ├── attendance_manager.py       # Attendance session manager
│   ├── camera.py                   # Camera handling
│   ├── database.py                 # SQLite database operations
│   ├── face_recognition_module.py  # Face recognition logic
│   ├── logger.py                   # Logging setup
│   ├── ui.py                       # Tkinter UI
│   └── utils.py                    # Utility functions
├── dataset/                        # Employee photos (INCLUDED)
│   ├── Ali/                        # 34 photos
│   ├── Amirreza/                   # 30 photos
│   ├── Benyamin/                   # 30 photos
│   ├── Hamidreza/                  # 34 photos
│   ├── Kian/                       # 30 photos
│   ├── Mahdi/                      # 36 photos
│   ├── Mohammad/                   # 32 photos
│   └── Mojtaba/                    # 31 photos
├── data/                           # Data directory
│   ├── faces.pkl                   # Face encodings (auto-generated)
│   └── attendance.db               # Attendance database (auto-generated)
└── logs/                           # Log files
    └── attendance.log              # Application logs (auto-generated)
```

## Installation

### Step 1: Install Python

Download and install Python 3.7, 3.8, or 3.9 from https://www.python.org/downloads/

**Important**: During installation, check "Add Python to PATH"

### Step 2: Install Visual C++ Build Tools (Required for dlib)

Download and install:
- Microsoft Visual C++ 14.0 or greater
- Get it from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Install "Desktop development with C++" workload

### Step 3: Install CMake (Required for dlib)

Download and install CMake from: https://cmake.org/download/

Add CMake to system PATH during installation.

### Step 4: Install Python Dependencies

Open Command Prompt and navigate to project directory:

```bash
cd FaceAttendanceSystem
```

Install dependencies:

```bash
pip install -r requirements.txt
```

**Note**: Installation may take 10-30 minutes on old hardware, especially for dlib.

If dlib installation fails, try:
```bash
pip install dlib-binary
```

## Quick Start

### Step 1: Build Face Encodings

The dataset with 8 employees is already included in the project.

Build face encodings:

```bash
python build_embeddings.py
```

Or double-click: `build_encodings.bat`

This will:
- Process all 8 employees (257 photos total)
- Create face encodings
- Save to `data/faces.pkl`

### Step 2: Run Application

```bash
python app.py
```

Or double-click: `run_app.bat`

## Dataset Information

### Current Employees (8 total)

The project includes photos for 8 employees:

1. **Ali** - 34 photos
2. **Amirreza** - 30 photos
3. **Benyamin** - 30 photos
4. **Hamidreza** - 34 photos
5. **Kian** - 30 photos
6. **Mahdi** - 36 photos
7. **Mohammad** - 32 photos
8. **Mojtaba** - 31 photos

**Total**: 257 photos across 8 employees

### Dataset Location

```
FaceAttendanceSystem/dataset/
```

All employee photos are included inside the project folder, making it completely portable.

## Adding New Employees

To add a new employee:

1. Create a new folder in `dataset/` with the employee's name:
   ```
   dataset/New_Employee_Name/
   ```

2. Add 3-5 clear photos (JPG, PNG, or BMP)

3. Rebuild encodings:
   ```bash
   python build_embeddings.py
   ```

4. Done! No code changes needed.

## Usage

### Main Window

The main window displays:
- Organization name
- Current date and time
- **CHECK IN** button (green)
- **CHECK OUT** button (red)
- **EXIT** button (gray)

### Workflow

1. Operator selects **CHECK IN** or **CHECK OUT**
2. Webcam opens automatically
3. Employee stands 50-120 cm from camera
4. System recognizes face automatically (2-5 seconds)
5. Attendance is saved to database
6. Success message displays employee name, time, and confidence
7. Webcam closes automatically
8. Returns to main menu

### Recognition Window

Shows:
- Live webcam feed
- Face detection rectangle (green = recognized, red = unknown)
- Employee name and confidence percentage
- FPS counter
- Remaining time countdown
- Instructions

Press **Q** or **ESC** to cancel recognition.

## Configuration

Edit `config.py` to customize settings:

### Camera Settings

```python
CAMERA_ID = 0               # Camera device ID (0 = default)
CAMERA_WIDTH = 640          # Preferred resolution width
CAMERA_HEIGHT = 480         # Preferred resolution height
FALLBACK_WIDTH = 320        # Fallback resolution width
FALLBACK_HEIGHT = 240       # Fallback resolution height
```

### Recognition Settings

```python
RECOGNITION_MODEL = "hog"           # Detection model (use "hog" only)
RECOGNITION_TOLERANCE = 0.6         # Lower = stricter (0.0 - 1.0)
FACE_DETECTION_UPSAMPLE = 0         # Upsample times (0 = fastest)
FRAME_SKIP = 2                      # Process every Nth frame
```

### Timeout Settings

```python
RECOGNITION_TIMEOUT = 15    # Timeout in seconds
```

## Database

### Database Location

```
data/attendance.db
```

### Table Structure

```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT NOT NULL,
    employee_name TEXT NOT NULL,
    check_type TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    confidence REAL NOT NULL,
    camera_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Viewing Records

Use any SQLite viewer or command:

```bash
sqlite3 data/attendance.db "SELECT * FROM attendance ORDER BY timestamp DESC LIMIT 10;"
```

## Utility Scripts

### System Check

Verify system requirements and configuration:

```bash
python system_check.py
```

Or double-click: `system_check.bat`

### Export Attendance

Export attendance records to CSV:

```bash
python export_attendance.py
```

Or double-click: `export_attendance.bat`

Options:
- Export today's records
- Export this week's records
- Export this month's records
- Export all records
- Export custom date range
- View today's summary

## Logs

### Log Location

```
logs/attendance.log
```

### Log Contents

- Application startup/shutdown
- Attendance records
- Recognition events
- Unknown face detections
- Errors and warnings
- Camera events

## Portable Deployment

This project is **completely self-contained**:

✓ Dataset included inside project folder
✓ All code and configuration included
✓ No external dependencies on filesystem

To deploy on another computer:

1. Copy the entire `FaceAttendanceSystem` folder
2. Install Python and dependencies
3. Run `python build_embeddings.py` (to rebuild encodings)
4. Run `python app.py`

The project will work immediately without any path changes!

## Troubleshooting

### Camera Not Opening

- Check USB connection
- Try different `CAMERA_ID` in config.py (0, 1, 2...)
- Close other applications using webcam
- Restart computer

### No Face Encodings Found

- Run `python build_embeddings.py` first
- Check that dataset folder contains employee photos
- Verify photos are in correct format (JPG, PNG, BMP)

### Recognition Too Slow

- Increase `FRAME_SKIP` in config.py (try 3 or 4)
- Lower camera resolution to 320x240
- Close other applications
- Use HOG model only (already default)

### Poor Recognition Accuracy

- Add more photos per employee
- Use better quality photos
- Adjust `RECOGNITION_TOLERANCE` (try 0.5 for stricter)
- Ensure good lighting during recognition
- Clean camera lens

### dlib Installation Failed

Try installing pre-built wheel:
```bash
pip install dlib-binary
```

Or download pre-compiled wheel from:
https://github.com/sachadee/Dlib

## Performance Optimization

For old hardware:

1. **Frame Skip**: Increase `FRAME_SKIP` to 3 or 4
2. **Resolution**: Use 320x240 resolution
3. **Upsample**: Keep `FACE_DETECTION_UPSAMPLE = 0`
4. **Model**: Use HOG only (never CNN)
5. **Close Programs**: Close unnecessary applications
6. **Startup Items**: Disable startup programs

## License

This project is provided as-is for internal use.

## Credits

Built with:
- OpenCV: Computer vision library
- face_recognition: Face recognition library
- dlib: Machine learning toolkit
- SQLite: Database engine
- Tkinter: GUI framework

---

**Version**: 1.0  
**Last Updated**: 2024-06-13  
**Optimized for**: Windows 7, 2GB RAM, Old Hardware  
**Employees**: 8 (Ali, Amirreza, Benyamin, Hamidreza, Kian, Mahdi, Mohammad, Mojtaba)
