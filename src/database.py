import os
from datetime import datetime
from src.logger import get_logger

logger = get_logger()

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    import psycopg2
    import psycopg2.extras
    USE_POSTGRES = True
else:
    import sqlite3
    USE_POSTGRES = False


class AttendanceDatabase:

    def __init__(self, db_path=None):
        self.db_path = db_path
        self._create_database()

    def _get_conn(self):
        if USE_POSTGRES:
            return psycopg2.connect(DATABASE_URL)
        return __import__('sqlite3').connect(self.db_path)

    def _create_database(self):
        try:
            if USE_POSTGRES:
                conn = psycopg2.connect(DATABASE_URL)
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS attendance (
                        id SERIAL PRIMARY KEY,
                        employee_id TEXT NOT NULL,
                        employee_name TEXT NOT NULL,
                        check_type TEXT NOT NULL,
                        date TEXT NOT NULL,
                        time TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        camera_id INTEGER NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            else:
                import sqlite3
                db_dir = os.path.dirname(self.db_path)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir)
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS attendance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        employee_id TEXT NOT NULL,
                        employee_name TEXT NOT NULL,
                        check_type TEXT NOT NULL,
                        date TEXT NOT NULL,
                        time TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        camera_id INTEGER NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

            conn.commit()
            conn.close()
            logger.info("Database initialized")

        except Exception as e:
            logger.error(f"Database creation error: {str(e)}")
            raise

    def add_attendance(self, employee_id, employee_name, check_type, confidence, camera_id):
        try:
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")

            conn = self._get_conn()
            cursor = conn.cursor()

            if USE_POSTGRES:
                cursor.execute('''
                    INSERT INTO attendance
                    (employee_id, employee_name, check_type, date, time, confidence, camera_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (employee_id, employee_name, check_type, date_str, time_str, confidence, camera_id))
            else:
                cursor.execute('''
                    INSERT INTO attendance
                    (employee_id, employee_name, check_type, date, time, confidence, camera_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (employee_id, employee_name, check_type, date_str, time_str, confidence, camera_id))

            conn.commit()
            conn.close()
            logger.info(f"Attendance saved: {employee_name} - {check_type}")
            return True

        except Exception as e:
            logger.error(f"Failed to save attendance: {str(e)}")
            return False

    def get_today_records(self, date=None):
        try:
            target_date = date if date else datetime.now().strftime("%Y-%m-%d")

            conn = self._get_conn()
            cursor = conn.cursor()

            if USE_POSTGRES:
                cursor.execute('''
                    SELECT employee_name, check_type, date, time, confidence
                    FROM attendance
                    WHERE date = %s
                    ORDER BY time DESC
                ''', (target_date,))
            else:
                cursor.execute('''
                    SELECT employee_name, check_type, date, time, confidence
                    FROM attendance
                    WHERE date = ?
                    ORDER BY time DESC
                ''', (target_date,))

            records = cursor.fetchall()
            conn.close()

            return [
                {
                    "name": row[0],
                    "check_type": row[1],
                    "date": row[2],
                    "time": row[3],
                    "confidence": row[4],
                }
                for row in records
            ]

        except Exception as e:
            logger.error(f"Failed to retrieve attendance: {str(e)}")
            return []

    def get_today_attendance(self):
        return self.get_today_records()

    def get_employee_last_check(self, employee_name):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            conn = self._get_conn()
            cursor = conn.cursor()

            if USE_POSTGRES:
                cursor.execute('''
                    SELECT check_type, time FROM attendance
                    WHERE employee_name = %s AND date = %s
                    ORDER BY time DESC LIMIT 1
                ''', (employee_name, today))
            else:
                cursor.execute('''
                    SELECT check_type, time FROM attendance
                    WHERE employee_name = ? AND date = ?
                    ORDER BY time DESC LIMIT 1
                ''', (employee_name, today))

            record = cursor.fetchone()
            conn.close()
            return record

        except Exception as e:
            logger.error(f"Failed to retrieve last check: {str(e)}")
            return None
