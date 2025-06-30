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

        # Title centered above the form
        tk.Label(settings_frame, text="Arduino Configuration", font=("Helvetica", 14, "bold"), bg="white")\
            .pack(pady=(10, 15))

        # Inner frame to center form content
        form_frame = tk.Frame(settings_frame, bg="white")
        form_frame.pack()

        # Port label
        tk.Label(form_frame, text="Select Arduino Port:", bg="white", font=("Helvetica", 11))\
            .grid(row=0, column=0, sticky="e", padx=(10, 5), pady=5)

        # Port dropdown
        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(form_frame, textvariable=self.port_var, state="readonly", width=15)
        self.port_dropdown.grid(row=0, column=1, sticky="w", padx=(0, 5), pady=5)

        # Refresh button next to dropdown
        refresh_btn = tk.Button(form_frame, text="⟳", command=self.refresh_ports_async,
                                font=("Helvetica", 11), bg="white", relief="flat", bd=0)
        refresh_btn.grid(row=0, column=2, sticky="w", padx=(0, 10), pady=5)

        # Status label centered below
        self.status_label = tk.Label(settings_frame, text="", fg="green", bg="white", font=("Helvetica", 10, "italic"))
        self.status_label.pack(pady=5)

        # Connect button centered below
        connect_btn = ttk.Button(settings_frame, text="Connect", command=self.connect_async)
        connect_btn.pack(pady=10)

        # Arduino Data Page
        arduino_page_btn = ttk.Button(self.container, text="Arduino Data Page",
                                      command=lambda: controller.show_frame("ArduinoDataPage"))
        arduino_page_btn.pack(pady=10)

        # Start Button
        self.start_btn = ttk.Button(self.container, text="Start",
                                   command=lambda: controller.show_frame("ExerciseSelectionPage"))
        self.start_btn.pack(pady=10)

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
