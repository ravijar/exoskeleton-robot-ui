import tkinter as tk
from service.arduino_comm import send_to_arduino, read_xyz_loop
from ui.back_button_mixin import BackButtonMixin

class ArduinoDataPage(tk.Frame, BackButtonMixin):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller

        tk.Label(self, text="Arduino Sensor Data", font=("Arial", 16)).pack(pady=10)
        self.xyz_label = tk.Label(self, text="X: -- Y: -- Z: --", font=("Arial", 14))
        self.xyz_label.pack(pady=10)

        self.led_button = tk.Button(self, text="Turn ON LED", command=self.toggle_led)
        self.led_button.pack(pady=10)
        self.led_on = False

        self.add_back_button(self, controller)

        read_xyz_loop(self.update_xyz_display)

    def update_xyz_display(self, x, y, z):
        self.xyz_label.config(text=f"X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}")

    def toggle_led(self):
        self.led_on = not self.led_on
        if self.led_on:
            send_to_arduino("LED_ON")
            self.led_button.config(text="Turn OFF LED")
        else:
            send_to_arduino("LED_OFF")
            self.led_button.config(text="Turn ON LED")
