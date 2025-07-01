import tkinter as tk
from ui.back_button_mixin import BackButtonMixin
from service.high_level_controller import init_enc_value, get_curr_angle, update_curr_angle

class ArduinoDataPage(tk.Frame, BackButtonMixin):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller

        tk.Label(self, text="Data Communication", font=("Arial", 16)).pack(pady=20)

        self.curr_angle_label = tk.Label(self, text=f"Current Angle: {get_curr_angle():.2f}", font=("Arial", 12))
        self.curr_angle_label.pack(pady=10)

        self.read_btn = tk.Button(self, text="Calculate Current Angle", command=self.update_ui)
        self.read_btn.pack(pady=10)

        self.add_back_button(self, controller)

    def on_show(self):
        init_enc_value()
        

    def update_ui(self):
        update_curr_angle(lambda angle: self.curr_angle_label.config(text=f"Current Angle: {angle:.2f}°"))


