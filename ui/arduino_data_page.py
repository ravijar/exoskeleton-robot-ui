import tkinter as tk
from ui.back_button_mixin import BackButtonMixin
import service.high_level_controller as hlc

class ArduinoDataPage(tk.Frame, BackButtonMixin):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller

        tk.Label(self, text="Data Communication", font=("Arial", 16)).pack(pady=20)

        self.curr_angle_label = tk.Label(self, text=f"Current Angle: {hlc.get_curr_angle():.2f}", font=("Arial", 12))
        self.curr_angle_label.pack(pady=10)

        self.read_btn = tk.Button(self, text="Calculate Current Angle", command=self.update_ui)
        self.read_btn.pack(pady=10)

        self.reps_var = tk.IntVar(value=1)
        self.reps_dropdown = tk.OptionMenu(
            self,
            self.reps_var,
            *[1, 2, 4, 6, 8, 10, 12],
            command=lambda val: hlc.set_number_of_reps(int(val))
        )
        self.reps_dropdown.pack(pady=10)

        self.run_btn = tk.Button(self, text="Run Exercise", command=hlc.run_exercise)
        self.run_btn.pack(pady=10)

        self.add_back_button(self, controller)

    def on_show(self):
        hlc.init_enc_value()
        

    def update_ui(self):
        hlc.update_curr_angle(lambda angle: self.curr_angle_label.config(text=f"Current Angle: {angle:.2f}°"))


