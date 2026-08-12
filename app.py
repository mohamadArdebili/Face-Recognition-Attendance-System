import cv2
import base64
import numpy as np
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import config
from src.face_recognition_module import FaceRecognizer
from src.database import AttendanceDatabase
from src.logger import get_logger

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "Xk9#mP2$qL7@nR4!vT6")

REPORT_PASSWORD = os.environ.get("REPORT_PASSWORD", "")

logger = get_logger()
recognizer = FaceRecognizer(
    encodings_path=config.ENCODINGS_PATH,
    tolerance=config.RECOGNITION_TOLERANCE,
    model=config.RECOGNITION_MODEL,
    upsample=config.FACE_DETECTION_UPSAMPLE
)
database = AttendanceDatabase(config.DATABASE_PATH)


@app.route("/")
def index():
    return render_template("index.html", org_name=config.ORGANIZATION_NAME)


@app.route("/recognize", methods=["POST"])
def recognize():
    data = request.get_json()
    check_type = data.get("check_type")
    image_b64 = data.get("image")
    if not check_type or not image_b64:
        return jsonify({"success": False, "message": "Missing parameters"}), 400
    try:
        header, encoded = image_b64.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except Exception as e:
        return jsonify({"success": False, "message": f"Image decode error: {e}"}), 400

    name, confidence, face_location = recognizer.recognize_face(frame)

    face_box = None
    if face_location:
        top, right, bottom, left = face_location
        face_box = {"top": top, "right": right, "bottom": bottom, "left": left}

    if name is None:
        return jsonify({"success": False, "message": "No face detected", "face_box": face_box})
    if name == "Unknown":
        return jsonify({"success": False, "message": "Face not recognized", "face_box": face_box})

    saved = database.add_attendance(
        employee_id=name,
        employee_name=name,
        check_type=check_type,
        confidence=confidence,
        camera_id=config.CAMERA_ID
    )
    if saved:
        logger.info(
            f"Attendance saved: {name} - {check_type} ({confidence:.2%})")
        return jsonify({
            "success":       True,
            "employee_name": name,
            "confidence":    f"{confidence:.1%}",
            "check_type":    check_type,
            "face_box":      face_box
        })
    else:
        return jsonify({"success": False, "message": "Database error", "face_box": face_box})


# ── Report auth ────────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == REPORT_PASSWORD:
            session["authenticated"] = True
            return redirect(url_for("report"))
        error = "رمز عبور اشتباه است."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/report")
def report():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return render_template("report.html")


@app.route('/api/records')
def api_records():
    if not session.get("authenticated"):
        return jsonify({"error": "Unauthorized"}), 401
    date = request.args.get('date')
    records = database.get_today_records(date)
    return jsonify({'records': records})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
