import tkinter as tk
from service.arduino_comm import send_to_arduino, read_response_async
from ui.back_button_mixin import BackButtonMixin
from service.high_level_controller import set_initial_encoder_value, set_curr_angle, get_curr_angle

class ArduinoDataPage(tk.Frame, BackButtonMixin):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller

        tk.Label(self, text="Data Communication", font=("Arial", 16)).pack(pady=20)

        self.curr_angle_label = tk.Label(self, text="Current Angle: --", font=("Arial", 12))
        self.curr_angle_label.pack(pady=10)

        self.read_btn = tk.Button(self, text="Calculate Current Angle", command=self.update_current_angle)
        self.read_btn.pack(pady=10)

        self.add_back_button(self, controller)

    def on_show(self):
        self.get_encoder_value(set_initial_encoder_value)

    def get_encoder_value(self, callback):
        send_to_arduino("GET_ENCODER_VALUE")

        def handle_response(value_str):
            try:
                value = int(value_str)
                callback(value)
            except ValueError:
                print("Invalid encoder value:", value_str)

        read_response_async(handle_response, expected_prefix="ENCODER_VALUE")
        

    def update_current_angle(self):
        self.get_encoder_value(set_curr_angle)
        self.curr_angle_label.config(text=f"Current Angle: {get_curr_angle()}")

