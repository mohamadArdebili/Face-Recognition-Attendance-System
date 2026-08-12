import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import threading
import queue
from src.logger import get_logger


class AttendanceUI:
    def __init__(self, config, attendance_manager):
        self.config = config
        self.attendance_manager = attendance_manager
        self.logger = get_logger()

        self.root = tk.Tk()
        self.root.title(config.ORGANIZATION_NAME)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.resizable(False, False)

        self._center_window()

        self.time_label = None
        self.date_label = None

        # Queue for passing check_type from button click to main loop
        self._session_queue = queue.Queue()

        self._create_ui()
        self._update_datetime()

    def _center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def _create_ui(self):
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = tk.Label(
            main_frame,
            text=self.config.ORGANIZATION_NAME,
            font=('Arial', 24, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=30)

        datetime_frame = tk.Frame(main_frame, bg='#2c3e50')
        datetime_frame.pack(pady=20)

        self.date_label = tk.Label(
            datetime_frame,
            text="",
            font=('Arial', 18),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        self.date_label.pack()

        self.time_label = tk.Label(
            datetime_frame,
            text="",
            font=('Arial', 36, 'bold'),
            bg='#2c3e50',
            fg='#3498db'
        )
        self.time_label.pack()

        buttons_frame = tk.Frame(main_frame, bg='#2c3e50')
        buttons_frame.pack(pady=40)

        check_in_btn = tk.Button(
            buttons_frame,
            text="CHECK IN",
            font=('Arial', 20, 'bold'),
            bg='#27ae60',
            fg='white',
            width=15,
            height=2,
            command=lambda: self._request_session("CHECK IN"),
            cursor='hand2'
        )
        check_in_btn.pack(pady=10)

        check_out_btn = tk.Button(
            buttons_frame,
            text="CHECK OUT",
            font=('Arial', 20, 'bold'),
            bg='#e74c3c',
            fg='white',
            width=15,
            height=2,
            command=lambda: self._request_session("CHECK OUT"),
            cursor='hand2'
        )
        check_out_btn.pack(pady=10)

        exit_btn = tk.Button(
            buttons_frame,
            text="EXIT",
            font=('Arial', 16),
            bg='#95a5a6',
            fg='white',
            width=15,
            height=1,
            command=self._exit_application,
            cursor='hand2'
        )
        exit_btn.pack(pady=20)

        footer_label = tk.Label(
            main_frame,
            text="Stand 50-120 cm from camera for best results",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#95a5a6'
        )
        footer_label.pack(side=tk.BOTTOM, pady=10)

    def _update_datetime(self):
        now = datetime.now()
        self.date_label.config(text=now.strftime("%A, %B %d, %Y"))
        self.time_label.config(text=now.strftime("%H:%M:%S"))
        self.root.after(1000, self._update_datetime)

    def _request_session(self, check_type):
        """
        Called from button click (main thread).
        Puts check_type in queue so the polling loop picks it up.
        """
        self.logger.info(f"User selected: {check_type}")
        self._session_queue.put(check_type)

    def _poll_session_queue(self):
        """
        Runs on main thread via root.after().
        Picks up pending session requests and runs them synchronously.
        """
        try:
            check_type = self._session_queue.get_nowait()
            self._run_session(check_type)
        except queue.Empty:
            pass
        finally:
            # Re-schedule unless app is closing
            if self.root.winfo_exists():
                self.root.after(100, self._poll_session_queue)

    def _run_session(self, check_type):
        """
        Runs entirely on main thread — safe for both tkinter and OpenCV.
        """
        self.root.withdraw()
        self.root.update()   # flush withdraw before OpenCV window appears

        success, employee_name, confidence, error_msg = \
            self.attendance_manager.start_session(check_type)

        self.root.deiconify()
        self.root.update()

        if success:
            self._show_success(employee_name, confidence, check_type)
        else:
            self._show_error(error_msg)

    def _show_success(self, employee_name, confidence, check_type):
        now = datetime.now()
        message = (
            f"Attendance Saved Successfully!\n\n"
            f"Employee: {employee_name}\n"
            f"Action: {check_type}\n"
            f"Date: {now.strftime('%Y-%m-%d')}\n"
            f"Time: {now.strftime('%H:%M:%S')}\n"
            f"Confidence: {confidence:.1%}"
        )
        messagebox.showinfo("Success", message)
        self.logger.info(f"Success message shown for {employee_name}")

    def _show_error(self, error_msg):
        if error_msg and error_msg != "Cancelled by user":
            messagebox.showerror("Error", error_msg)
            self.logger.error(f"Error message shown: {error_msg}")

    def _exit_application(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.logger.info("Application closed by user")
            self.attendance_manager.cleanup()
            self.root.quit()
            self.root.destroy()

    def run(self):
        self.logger.info("UI started")
        self.root.protocol("WM_DELETE_WINDOW", self._exit_application)
        # Start polling loop
        self.root.after(100, self._poll_session_queue)
        self.root.mainloop()
