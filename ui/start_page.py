import tkinter as tk
from tkinter import ttk
from service.arduino_comm import list_serial_ports, connect_to_arduino

class StartPage(tk.Frame):
    def __init__(self, controller):
        super().__init__(controller, bg="#f0f2f5")

        # Configure full frame grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Main container (centered)
        container = tk.Frame(self, bg="#f0f2f5")
        container.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)

        # Title
        title = tk.Label(container, text="Rehabilitation Exoskeleton",
                         font=("Helvetica", 24, "bold"), bg="#f0f2f5", fg="#333")
        title.grid(row=0, column=0, pady=(0, 30))

        # Arduino Settings Group
        settings_frame = tk.Frame(container, bg="white", bd=2, relief="groove")
        settings_frame.grid(row=1, column=0, sticky="ew", pady=(0, 30), ipadx=20, ipady=20)

        tk.Label(settings_frame, text="Arduino Configuration", font=("Helvetica", 14, "bold"), bg="white")\
            .grid(row=0, column=0, columnspan=2, pady=(10, 15))

        tk.Label(settings_frame, text="Select Arduino Port:", bg="white", font=("Helvetica", 11))\
            .grid(row=1, column=0, sticky="e", padx=10, pady=5)

        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(settings_frame, textvariable=self.port_var, state="readonly", width=30)
        self.port_dropdown.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        refresh_btn = ttk.Button(settings_frame, text="🔄 Refresh Ports", command=self.refresh_ports)
        refresh_btn.grid(row=2, column=0, columnspan=2, pady=5)

        self.status_label = tk.Label(settings_frame, text="", fg="green", bg="white", font=("Helvetica", 10, "italic"))
        self.status_label.grid(row=3, column=0, columnspan=2, pady=5)

        connect_btn = ttk.Button(settings_frame, text="🔌 Connect to Arduino", command=self.connect)
        connect_btn.grid(row=4, column=0, columnspan=2, pady=(10, 0))

        # Arduino Data Page
        arduino_page_btn = ttk.Button(container, text="🧪 Open Arduino Data Page",
                                      command=lambda: controller.show_frame("ArduinoDataPage"))
        arduino_page_btn.grid(row=2, column=0, pady=10)

        # Start button (large, pinned at bottom)
        start_btn = tk.Button(self, text="▶ Start",
                              font=("Helvetica", 14, "bold"),
                              bg="#007BFF", fg="white",
                              activebackground="#0056b3",
                              relief="raised",
                              bd=3,
                              height=2, width=20,
                              command=lambda: controller.show_frame("ExerciseSelectionPage"))
        start_btn.grid(row=1, column=0, pady=(0, 30), sticky="s")

        # Adjust layout behavior
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.refresh_ports()

    def refresh_ports(self):
        ports = list_serial_ports()
        self.port_dropdown['values'] = ports
        if ports:
            self.port_dropdown.set(ports[0])
        else:
            self.port_dropdown.set('No ports found')

    def connect(self):
        port = self.port_var.get()
        if connect_to_arduino(port):
            self.status_label.config(text="✅ Connected", fg="green")
        else:
            self.status_label.config(text="❌ Connection failed", fg="red")
