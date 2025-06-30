import tkinter as tk
from tkinter import ttk
from service.arduino_comm import list_serial_ports, connect_to_arduino
import threading
import time

class StartPage(tk.Frame):
    def __init__(self, controller):
        super().__init__(controller, bg="#f0f2f5")

        # Centered layout using place and anchor
        self.container = tk.Frame(self, bg="#f0f2f5")
        self.container.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        title = tk.Label(self.container, text="Rehabilitation Exoskeleton",
                         font=("Helvetica", 24, "bold"), bg="#f0f2f5", fg="#333")
        title.pack(pady=(0, 30))

        # Arduino Settings Group
        settings_frame = tk.Frame(self.container, bg="white", bd=2, relief="groove")
        settings_frame.pack(pady=(0, 30), ipadx=20, ipady=20)

        tk.Label(settings_frame, text="Arduino Configuration", font=("Helvetica", 14, "bold"), bg="white")\
            .grid(row=0, column=0, columnspan=3, pady=(10, 15))

        # Dropdown + Refresh button in same row
        tk.Label(settings_frame, text="Select Arduino Port:", bg="white", font=("Helvetica", 11))\
            .grid(row=1, column=0, sticky="e", padx=(10, 5), pady=5)

        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(settings_frame, textvariable=self.port_var, state="readonly", width=15)
        self.port_dropdown.grid(row=1, column=1, sticky="w", padx=(0, 5), pady=5)

        refresh_btn = tk.Button(settings_frame, text="⟳", command=self.refresh_ports_async,
                                font=("Helvetica", 11), bg="white", relief="flat", bd=0)
        refresh_btn.grid(row=1, column=2, sticky="w", padx=(0, 10), pady=5)

        # Status & spinner
        self.status_label = tk.Label(settings_frame, text="", fg="green", bg="white", font=("Helvetica", 10, "italic"))
        self.status_label.grid(row=2, column=0, columnspan=3, pady=5)

        # Connect button
        connect_btn = ttk.Button(settings_frame, text="Connect to Arduino", command=self.connect_async)
        connect_btn.grid(row=3, column=0, columnspan=3, pady=(10, 0))

        # Arduino Data Page
        arduino_page_btn = ttk.Button(self.container, text="Arduino Data Page",
                                      command=lambda: controller.show_frame("ArduinoDataPage"))
        arduino_page_btn.pack(pady=10)

        # Start Button
        self.start_btn = tk.Button(self.container, text="Start",
                                   font=("Helvetica", 14, "bold"),
                                   bg="#3399FF", fg="white",
                                   activebackground="#66B3FF",
                                   relief="flat",
                                   bd=0,
                                   height=2, width=20,
                                   command=lambda: controller.show_frame("ExerciseSelectionPage"))
        self.start_btn.pack(pady=30)

        self.start_btn.configure(highlightthickness=0)
        self.start_btn.bind("<Enter>", lambda e: self.start_btn.config(bg="#66B3FF"))
        self.start_btn.bind("<Leave>", lambda e: self.start_btn.config(bg="#3399FF"))

        self.refresh_ports_async()

    def set_status(self, text, color="green"):
        self.status_label.config(text=text, fg=color)

    def refresh_ports_async(self):
        def task():
            self.set_status("⏳ Refreshing...")
            ports = list_serial_ports()
            time.sleep(0.5)  # mimic spinner duration
            self.port_dropdown['values'] = ports
            if ports:
                self.port_dropdown.set(ports[0])
                self.set_status("✅ Ports loaded")
            else:
                self.port_dropdown.set('No ports found')
                self.set_status("⚠️ No ports found", color="orange")

        threading.Thread(target=task).start()

    def connect_async(self):
        def task():
            port = self.port_var.get()
            self.set_status("⏳ Connecting...")
            success = connect_to_arduino(port)
            time.sleep(0.5)  # mimic spinner duration
            if success:
                self.set_status("✅ Connected", color="green")
            else:
                self.set_status("❌ Connection failed", color="red")

        threading.Thread(target=task).start()
