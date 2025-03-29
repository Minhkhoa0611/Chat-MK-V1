import subprocess
import tkinter as tk
from tkinter import ttk
from threading import Thread
import os
import webbrowser
import json  # Add import for JSON to handle saving and loading window size

class ServerManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Server Manager")
        self.root.configure(bg="#2c3e50")  # Set background color

        # Load window size from file
        self.load_window_size()

        # Bind resize event to update the title with window size
        self.root.bind("<Configure>", self.update_title_with_size)

        # Create frames for each server
        self.server1_frame = ttk.LabelFrame(root, text="Flask Web Server", style="Custom.TLabelframe")
        self.server2_frame = ttk.LabelFrame(root, text="Node.js Web Server", style="Custom.TLabelframe")
        self.server3_frame = ttk.LabelFrame(root, text="Flask Web Server v2", style="Custom.TLabelframe")
        self.server4_frame = ttk.LabelFrame(root, text="Node.js Web Server v2", style="Custom.TLabelframe")

        # Configure grid weights for responsiveness
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Adjust frames to expand with the window
        self.server1_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.server2_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.server3_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.server4_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Configure frame grid weights
        self.server1_frame.grid_rowconfigure(0, weight=1)
        self.server1_frame.grid_columnconfigure(0, weight=1)
        self.server2_frame.grid_rowconfigure(0, weight=1)
        self.server2_frame.grid_columnconfigure(0, weight=1)
        self.server3_frame.grid_rowconfigure(0, weight=1)
        self.server3_frame.grid_columnconfigure(0, weight=1)
        self.server4_frame.grid_rowconfigure(0, weight=1)
        self.server4_frame.grid_columnconfigure(0, weight=1)

        # Create text widgets for server logs
        self.server1_log = tk.Text(self.server1_frame, height=20, width=50, state="disabled", bg="#ecf0f1", fg="#2c3e50")
        self.server2_log = tk.Text(self.server2_frame, height=20, width=50, state="disabled", bg="#ecf0f1", fg="#2c3e50")
        self.server3_log = tk.Text(self.server3_frame, height=20, width=50, state="disabled", bg="#ecf0f1", fg="#2c3e50")
        self.server4_log = tk.Text(self.server4_frame, height=20, width=50, state="disabled", bg="#ecf0f1", fg="#2c3e50")

        # Place log widgets inside frames
        self.server1_log.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.server2_log.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.server3_log.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.server4_log.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Create button frames for better layout
        self.server1_button_frame = ttk.Frame(self.server1_frame)
        self.server1_button_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.server2_button_frame = ttk.Frame(self.server2_frame)
        self.server2_button_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.server3_button_frame = ttk.Frame(self.server3_frame)
        self.server3_button_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.server4_button_frame = ttk.Frame(self.server4_frame)
        self.server4_button_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        # Create start/stop buttons for each server
        self.server1_start_button = ttk.Button(self.server1_button_frame, text="Start Server", command=self.start_server1)
        self.server1_stop_button = ttk.Button(self.server1_button_frame, text="Stop Server", command=self.stop_server1, state="disabled")
        self.server1_refresh_button = ttk.Button(self.server1_button_frame, text="Refresh Logs", command=lambda: self.refresh_logs(self.server1_log))

        self.server2_start_button = ttk.Button(self.server2_button_frame, text="Start Server", command=self.start_server2)
        self.server2_stop_button = ttk.Button(self.server2_button_frame, text="Stop Server", command=self.stop_server2, state="disabled")
        self.server2_refresh_button = ttk.Button(self.server2_button_frame, text="Refresh Logs", command=lambda: self.refresh_logs(self.server2_log))

        self.server3_start_button = ttk.Button(self.server3_button_frame, text="Start Server", command=self.start_server3)
        self.server3_stop_button = ttk.Button(self.server3_button_frame, text="Stop Server", command=self.stop_server3, state="disabled")
        self.server3_refresh_button = ttk.Button(self.server3_button_frame, text="Refresh Logs", command=lambda: self.refresh_logs(self.server3_log))

        self.server4_start_button = ttk.Button(self.server4_button_frame, text="Start Server", command=self.start_server4)
        self.server4_stop_button = ttk.Button(self.server4_button_frame, text="Stop Server", command=self.stop_server4, state="disabled")
        self.server4_refresh_button = ttk.Button(self.server4_button_frame, text="Refresh Logs", command=lambda: self.refresh_logs(self.server4_log))

        # Add buttons to button frames
        self.server1_start_button.pack(side="left", padx=5, pady=5)
        self.server1_stop_button.pack(side="left", padx=5, pady=5)
        self.server1_refresh_button.pack(side="left", padx=5, pady=5)

        self.server2_start_button.pack(side="left", padx=5, pady=5)
        self.server2_stop_button.pack(side="left", padx=5, pady=5)
        self.server2_refresh_button.pack(side="left", padx=5, pady=5)

        self.server3_start_button.pack(side="left", padx=5, pady=5)
        self.server3_stop_button.pack(side="left", padx=5, pady=5)
        self.server3_refresh_button.pack(side="left", padx=5, pady=5)

        self.server4_start_button.pack(side="left", padx=5, pady=5)
        self.server4_stop_button.pack(side="left", padx=5, pady=5)
        self.server4_refresh_button.pack(side="left", padx=5, pady=5)

        # Add server status indicators
        self.server1_status = ttk.Label(self.server1_frame, text="Status: Stopped", foreground="red", style="Custom.TLabel")
        self.server2_status = ttk.Label(self.server2_frame, text="Status: Stopped", foreground="red", style="Custom.TLabel")
        self.server3_status = ttk.Label(self.server3_frame, text="Status: Stopped", foreground="red", style="Custom.TLabel")
        self.server4_status = ttk.Label(self.server4_frame, text="Status: Stopped", foreground="red", style="Custom.TLabel")

        # Add status labels below buttons
        self.server1_status.grid(row=2, column=0, sticky="ew", pady=5)
        self.server2_status.grid(row=2, column=0, sticky="ew", pady=5)
        self.server3_status.grid(row=2, column=0, sticky="ew", pady=5)
        self.server4_status.grid(row=2, column=0, sticky="ew", pady=5)

        # Initialize server processes
        self.server1_process = None
        self.server2_process = None
        self.server3_process = None
        self.server4_process = None

        # Apply custom styles
        self.apply_styles()

    def apply_styles(self):
        """Apply custom styles for the GUI."""
        style = ttk.Style()
        style.configure("Custom.TLabelframe", background="#34495e", foreground="#ecf0f1", font=("Arial", 12, "bold"))
        style.configure("Custom.TLabel", background="#34495e", foreground="#ecf0f1", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10))

    def update_title_with_size(self, event=None):
        """Update the window title with the current size and author information."""
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        self.root.title(f"Server Manager - {width}x{height} | CODER: BY MINH KHOA, WEBSITE: XAYDUNGMINHKHOA.ONLINE")

    def load_window_size(self):
        """Load the window size from a file."""
        try:
            with open("window_size.json", "r") as f:
                size = json.load(f)
                self.root.geometry(f"{size['width']}x{size['height']}")
                self.update_title_with_size()  # Update title after setting size
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            self.update_title_with_size()  # Default title if no size is loaded

    def save_window_size(self):
        """Save the current window size to a file."""
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        with open("window_size.json", "w") as f:
            json.dump({"width": width, "height": height}, f)

    def start_server1(self):
        """Start the Flask Web Server."""
        if self.server1_process is None:
            self.server1_process = subprocess.Popen(
                ["python", os.path.join(os.getcwd(), "file_transfer_server.py")],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.server1_start_button.config(state="disabled")
            self.server1_stop_button.config(state="normal")
            self.server1_status.config(text="Status: Running", foreground="green")
            Thread(target=self.update_log, args=(self.server1_process, self.server1_log)).start()

            # Open the server address in a new Chrome window
            Thread(target=lambda: os.system(f'start chrome --new-window http://localhost:8002')).start()

    def stop_server1(self):
        """Stop the Flask Web Server."""
        if self.server1_process:
            self.server1_process.terminate()
            self.server1_process = None
            self.server1_start_button.config(state="normal")
            self.server1_stop_button.config(state="disabled")
            self.server1_status.config(text="Status: Stopped", foreground="red")

    def start_server2(self):
        """Start the Node.js Web Server."""
        if self.server2_process is None:
            self.server2_process = subprocess.Popen(
                ["node", os.path.join(os.getcwd(), "file_transfer_server.js")],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.server2_start_button.config(state="disabled")
            self.server2_stop_button.config(state="normal")
            self.server2_status.config(text="Status: Running", foreground="green")
            Thread(target=self.update_log, args=(self.server2_process, self.server2_log)).start()

            # Open the server address in a new Chrome window
            Thread(target=lambda: os.system(f'start chrome --new-window http://localhost:8001')).start()

    def stop_server2(self):
        """Stop the Node.js Web Server."""
        if self.server2_process:
            self.server2_process.terminate()
            self.server2_process = None
            self.server2_start_button.config(state="normal")
            self.server2_stop_button.config(state="disabled")
            self.server2_status.config(text="Status: Stopped", foreground="red")

    def start_server3(self):
        """Start the Flask Web Server v2."""
        if self.server3_process is None:
            self.server3_process = subprocess.Popen(
                ["python", os.path.join(os.getcwd(), "file_transfer_server_v2.py")],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.server3_start_button.config(state="disabled")
            self.server3_stop_button.config(state="normal")
            self.server3_status.config(text="Status: Running", foreground="green")
            Thread(target=self.update_log, args=(self.server3_process, self.server3_log)).start()

            # Open the server address in a new Chrome window
            Thread(target=lambda: os.system(f'start chrome --new-window http://localhost:8003')).start()

    def stop_server3(self):
        """Stop the Flask Web Server v2."""
        if self.server3_process:
            self.server3_process.terminate()
            self.server3_process = None
            self.server3_start_button.config(state="normal")
            self.server3_stop_button.config(state="disabled")
            self.server3_status.config(text="Status: Stopped", foreground="red")

    def start_server4(self):
        """Start the Node.js Web Server v2."""
        if self.server4_process is None:
            self.server4_process = subprocess.Popen(
                ["node", os.path.join(os.getcwd(), "file_transfer_server_v2.js")],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.server4_start_button.config(state="disabled")
            self.server4_stop_button.config(state="normal")
            self.server4_status.config(text="Status: Running", foreground="green")
            Thread(target=self.update_log, args=(self.server4_process, self.server4_log)).start()

            # Open the server address in a new Chrome window
            Thread(target=lambda: os.system(f'start chrome --new-window http://localhost:2306')).start()

    def stop_server4(self):
        """Stop the Node.js Web Server v2."""
        if self.server4_process:
            self.server4_process.terminate()
            self.server4_process = None
            self.server4_start_button.config(state="normal")
            self.server4_stop_button.config(state="disabled")
            self.server4_status.config(text="Status: Stopped", foreground="red")

    def update_log(self, process, log_widget):
        """Update the log widget with server output."""
        for line in iter(process.stdout.readline, ""):
            log_widget.config(state="normal")
            log_widget.insert("end", line)
            log_widget.see("end")
            log_widget.config(state="disabled")

        process.stdout.close()

    def refresh_logs(self, log_widget):
        """Clear and refresh the logs."""
        log_widget.config(state="normal")
        log_widget.delete("1.0", "end")
        log_widget.config(state="disabled")

    def on_close(self):
        """Handle application close event."""
        self.save_window_size()  # Save window size before closing
        self.stop_server1()
        self.stop_server2()
        self.stop_server3()
        self.stop_server4()  # Stop server4
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerManagerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
