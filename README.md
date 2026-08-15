# Face Recognition Attendance System

A browser-based employee attendance system that uses face recognition to record check-ins and check-outs. The application provides a Persian (RTL) attendance interface, live webcam capture, an authenticated reporting dashboard, and support for SQLite or PostgreSQL.

## Features

- Browser-based webcam capture
- Face detection and recognition with `face_recognition` and dlib
- Check-in and check-out registration
- Recognition confidence display
- Password-protected administration dashboard
- Attendance filtering by date with a Jalali calendar
- Responsive Persian (RTL) user interface
- SQLite database for local use
- Optional PostgreSQL database for hosted deployments
- Incremental face-encoding generation
- CSV export utility for SQLite records
- Application and recognition event logging

## Technology Stack

- Python 3
- Flask and Gunicorn
- OpenCV
- face_recognition
- dlib
- NumPy
- SQLite or PostgreSQL
- HTML, CSS, and JavaScript

## How It Works

1. The user opens the attendance page and enables the browser camera.
2. The user selects check-in or check-out.
3. The browser captures one frame and sends it to the Flask application.
4. The server compares the first detected face with the stored encodings.
5. If a match is found, the attendance event is saved with its date, time, confidence score, and camera ID.
6. Authorized administrators can review records from the reporting dashboard.

Captured frames are processed for recognition and are not saved by the application.

## Project Structure

```text
.
├── app.py                         # Flask application and routes
├── build_embeddings.py            # Builds face encodings from the dataset
├── config.py                      # Application and recognition settings
├── export_attendance.py           # Interactive CSV export utility
├── system_check.py                # Local environment checks
├── requirements.txt               # Python dependencies
├── run.sh                         # Linux/macOS development launcher
├── run_app.bat                    # Windows launcher
├── wsgi.py                        # WSGI entry point
├── dataset/
│   └── Employee Name/             # Reference photos for one employee
├── data/
│   ├── faces.pkl                  # Generated face encodings
│   └── attendance.db              # Local SQLite database
├── logs/
│   └── attendance.log             # Runtime logs
├── src/
│   ├── database.py                # SQLite/PostgreSQL operations
│   ├── face_recognition_module.py # Face matching logic
│   ├── logger.py                  # Logging configuration
│   └── utils.py                   # Validation and export helpers
├── static/                        # Stylesheets and local assets
└── templates/
    ├── index.html                 # Attendance interface
    ├── login.html                 # Administrator login
    └── report.html                # Attendance reports
```

Runtime data, face images, encodings, logs, secrets, and exports are excluded from Git by the included `.gitignore`.

## Requirements

- Python 3.10 is recommended
- A webcam
- A modern browser with camera support
- CMake and a C/C++ build toolchain if a prebuilt dlib wheel is unavailable

For remote access, browsers normally require HTTPS before allowing webcam access. Camera access works on `localhost` during local development.

### Common system dependencies

On Debian or Ubuntu, the following packages may be required before installing the Python dependencies:

```bash
sudo apt update
sudo apt install build-essential cmake libopenblas-dev liblapack-dev
```

On Windows, install CMake and Microsoft Visual C++ Build Tools if dlib cannot be installed from a wheel.

## Installation

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd face_attendance-premium
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

Linux or macOS:

```bash
source venv/bin/activate
```

Windows Command Prompt:

```bat
venv\Scripts\activate
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```dotenv
SECRET_KEY=replace-with-a-long-random-value
REPORT_PASSWORD=replace-with-a-strong-admin-password

```

To use PostgreSQL, set `DATABASE_URL` in the process environment before starting the application:

```bash
export DATABASE_URL="postgresql://username:password@hostname:5432/database_name"
python app.py
```

When `DATABASE_URL` is omitted, the application uses the local SQLite database.

Always set a unique `SECRET_KEY` and `REPORT_PASSWORD` before exposing the application to other users. The fallback values in `app.py` are intended only for development and are not secure for deployment.

Recognition, camera, UI, path, and logging settings can be changed in `config.py`.

Important recognition options include:

```python
RECOGNITION_MODEL = "hog"
RECOGNITION_TOLERANCE = 0.6
FACE_DETECTION_UPSAMPLE = 0
CAMERA_ID = 0
```

A lower tolerance makes matching stricter. Test any change against representative photos before using it in production.

## Add Employees and Build Encodings

Create one directory per employee under `dataset/`. The directory name becomes the employee name stored in attendance records.

```text
dataset/
├── Alice Smith/
│   ├── photo-1.jpg
│   ├── photo-2.jpg
│   └── photo-3.jpg
└── Bob Jones/
    ├── photo-1.jpg
    └── photo-2.jpg
```

Supported image formats are JPG, JPEG, PNG, and BMP. Use clear, well-lit images containing one front-facing person.

Build the face encodings:

```bash
python build_embeddings.py
```

This creates `data/faces.pkl`. The builder works incrementally:

- New employee directories are encoded.
- Encodings for deleted employee directories are removed.
- Existing employees are skipped if they are already present.

If you replace or add photos for an already encoded employee, remove that employee's existing encodings or rebuild `data/faces.pkl` from scratch so the changed photos are processed.

## Run Locally

Start the Flask development server:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

The main attendance page is at `/`. The administration dashboard is at `/report` and redirects unauthenticated users to `/login`.

Linux and macOS users can also run:

```bash
./run.sh
```

Windows users can run:

```bat
run_app.bat
```

## Usage

### Record attendance

1. Open the home page.
2. Select the camera button.
3. Allow camera access in the browser.
4. Keep one face centered and clearly visible.
5. Select **Check In** or **Check Out** in the Persian interface.
6. Wait for the recognition result.

### View reports

1. Open `/report`.
2. Enter the password configured by `REPORT_PASSWORD`.
3. Select a date from the Jalali calendar to review its records.
4. Review check-in totals, check-out totals, and average recognition confidence.

## Database

The application automatically creates the `attendance` table.

When `DATABASE_URL` is not set, records are stored in:

```text
data/attendance.db
```

When `DATABASE_URL` is set, the application connects to PostgreSQL instead.

Each record contains:

- Employee ID
- Employee name
- Check type (`in` or `out`)
- Date
- Time
- Recognition confidence
- Camera ID
- Creation timestamp

Dates and times are generated from the application server's local clock.

## Export Attendance Records

For a local SQLite database, run:

```bash
python export_attendance.py
```

The interactive utility can export today's records, the current week, the current month, all records, or a custom date range to CSV.

The current export utility reads SQLite directly and does not use `DATABASE_URL`. PostgreSQL deployments should export records with PostgreSQL-compatible tools or extend the utility.

## Production Deployment

Run the WSGI application with Gunicorn:

```bash
gunicorn --bind 0.0.0.0:8000 --timeout 120 wsgi:application
```

Use a reverse proxy with HTTPS, especially when clients access the camera from another device. Also ensure that:

- `SECRET_KEY` and `REPORT_PASSWORD` are provided through environment variables.
- Persistent storage is configured for SQLite, encodings, and logs.
- `DATABASE_URL` points to a persistent PostgreSQL service when PostgreSQL is used.
- `data/faces.pkl` and the required employee encodings are present on the server.
- Access to attendance records and biometric data is restricted.

Each Gunicorn worker loads the face encodings into memory. Start with one worker on memory-constrained systems and scale only after measuring resource usage.

## HTTP Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/` | Attendance page |
| `POST` | `/recognize` | Recognizes a submitted frame and records attendance |
| `GET`, `POST` | `/login` | Administrator login |
| `GET` | `/logout` | Clears the administrator session |
| `GET` | `/report` | Protected reporting dashboard |
| `GET` | `/api/records` | Protected JSON attendance records, optionally filtered by `date=YYYY-MM-DD` |

## Troubleshooting

### Face encodings were not found

Run:

```bash
python build_embeddings.py
```

Confirm that `dataset/` contains at least one employee directory with valid images.

### The browser cannot access the camera

- Grant camera permission to the site.
- Close other applications that are using the webcam.
- Test with a current version of Chrome, Edge, or Firefox.
- Use `localhost` for local development or HTTPS for remote access.

### A face is not recognized

- Improve lighting and keep the face centered.
- Use clear reference photos with different natural angles.
- Confirm that the correct employee encoding exists.
- Adjust `RECOGNITION_TOLERANCE` carefully.

### dlib installation fails

- Install CMake and the platform's C/C++ build tools.
- Use a Python version for which a compatible dlib wheel is available.
- Upgrade `pip`, `setuptools`, and `wheel`, then retry the installation.

### Records do not appear in the report

- Confirm that the selected report date matches the server's local date.
- Check `logs/attendance.log`.
- Verify the SQLite file permissions or the PostgreSQL connection string.

## Privacy and Security

Face encodings and attendance records are sensitive biometric and employment data. Before deployment:

- Obtain any consent required in your jurisdiction.
- Limit access to the dataset, encodings, database, backups, and logs.
- Use HTTPS and strong credentials.
- Define retention and deletion policies.
- Do not commit `.env`, employee photos, databases, or generated encodings.
- Review the system for applicable privacy, labor, and biometric-data requirements.

## License

No open-source license is currently included. Unless a license is added, all rights are reserved by the project owner.
