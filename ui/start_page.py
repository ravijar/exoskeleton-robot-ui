import tkinter as tk
from tkinter import ttk
from service.arduino_comm import list_serial_ports, connect_to_arduino

class StartPage(tk.Frame):
    def __init__(self, controller):
        super().__init__(controller)

        tk.Label(self, text="Rehabilitation Exoskeleton", font=("Arial", 18)).pack(pady=40)

        # Port dropdown
        tk.Label(self, text="Select Arduino Port").pack()
        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(self, textvariable=self.port_var, state="readonly")
        self.port_dropdown.pack(pady=5)

        refresh_btn = tk.Button(self, text="Refresh Ports", command=self.refresh_ports)
        refresh_btn.pack()

        self.status_label = tk.Label(self, text="", fg="green")
        self.status_label.pack(pady=5)

        connect_btn = tk.Button(self, text="Connect to Arduino", command=self.connect)
        connect_btn.pack(pady=10)

        tk.Button(self, text="Start", command=lambda: controller.show_frame("ExerciseSelectionPage")).pack(pady=20)

        tk.Button(self, text="Arduino Data Page", command=lambda: controller.show_frame("ArduinoDataPage")).pack(pady=10)

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
