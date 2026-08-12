# How to Run Face Attendance System

## Quick Start

The project is now fully set up and ready to run!

### ✅ Setup Complete
- ✓ Virtual environment created (`venv/`)
- ✓ All dependencies installed
- ✓ Face encodings built (248 encodings from 8 employees)
- ✓ VS Code configuration ready

---

## Option 1: Run from VS Code (Recommended)

### Steps:
1. Open the project in VS Code:
   ```bash
   cd ~/Desktop/FaceAttendanceSystem
   code .
   ```

2. Press `F5` or go to **Run and Debug** (Ctrl+Shift+D)

3. Select **"Run Face Attendance System"** from the dropdown

4. Click the green play button

### Available Launch Configurations:
- **Run Face Attendance System** - Start the main application
- **Build Face Encodings** - Rebuild face encodings from dataset
- **Export Attendance Records** - Export attendance to CSV

---

## Option 2: Run from Terminal

### Using the run script:
```bash
cd ~/Desktop/FaceAttendanceSystem
./run.sh
```

### Or manually:
```bash
cd ~/Desktop/FaceAttendanceSystem
source venv/bin/activate
python app.py
```

---

## How to Use the Application

1. **Main Window** appears with three buttons:
   - CHECK IN (green)
   - CHECK OUT (red)
   - EXIT (gray)

2. Click **CHECK IN** or **CHECK OUT**

3. **Webcam opens automatically**

4. Employee stands 50-120 cm from camera

5. System recognizes face (2-5 seconds)

6. Attendance saved automatically

7. Success message shows employee name and time

8. Camera closes, returns to main menu

### Keyboard shortcuts in camera view:
- Press `Q` or `ESC` to cancel

---

## Project Information

### Dataset:
- **8 Employees**: Ali, Amirreza, Benyamin, Hamidreza, Kian, Mahdi, Mohammad, Mojtaba
- **248 face encodings** successfully created
- Located in: `dataset/`

### Database:
- SQLite database: `data/attendance.db`
- Stores all check-in/check-out records

### Logs:
- Application logs: `logs/attendance.log`

---

## Adding New Employees

1. Create folder: `dataset/NewEmployeeName/`
2. Add 3-5 clear photos (JPG, PNG, BMP)
3. Run: `python build_embeddings.py`
4. Done! No code changes needed

---

## Troubleshooting

### Camera not opening:
- Check USB connection
- Close other apps using webcam
- Try different camera ID in `config.py`

### Python environment issues:
```bash
source venv/bin/activate
pip list  # Verify packages installed
```

### Face not recognized:
- Ensure good lighting
- Stand 50-120 cm from camera
- Look directly at camera
- Add more photos to dataset and rebuild encodings

---

## System Requirements

- Python 3.12 (installed)
- Virtual environment with:
  - opencv-python
  - face-recognition
  - dlib
  - numpy
  - Pillow
  - setuptools

All dependencies are already installed in `venv/`.

---

## Contact

For issues, check:
1. `logs/attendance.log`
2. README.md (complete documentation)
3. Project documentation files

---

**Ready to run! Press F5 in VS Code or run `./run.sh`**
