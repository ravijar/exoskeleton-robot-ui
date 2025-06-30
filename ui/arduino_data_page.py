import tkinter as tk
from service.arduino_comm import send_to_arduino, read_response_async
from ui.back_button_mixin import BackButtonMixin

class ArduinoDataPage(tk.Frame, BackButtonMixin):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller

        tk.Label(self, text="Read Initial Encoder Value", font=("Arial", 16)).pack(pady=20)

        self.encoder_label = tk.Label(self, text="INIT_ENCODER: --", font=("Arial", 14))
        self.encoder_label.pack(pady=10)

        self.read_btn = tk.Button(self, text="Get Init Encoder", command=self.get_encoder_value)
        self.read_btn.pack(pady=10)

        self.add_back_button(self, controller)

    def get_encoder_value(self):
        self.encoder_label.config(text="INIT_ENCODER: ⏳")
        send_to_arduino("GET_INIT_ENCODER")
        read_response_async(self.handle_response, expected_prefix="INIT_ENCODER")

    def handle_response(self, value):
        self.encoder_label.config(text=f"INIT_ENCODER: {value}")
