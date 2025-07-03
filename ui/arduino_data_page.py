import tkinter as tk
from ui.back_button_mixin import BackButtonMixin
import service.new_high_level_controller as new_hlc

class ArduinoDataPage(tk.Frame, BackButtonMixin):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller

        tk.Label(self, text="Data Communication", font=("Arial", 16)).pack(pady=20)

        self.reps_var = tk.IntVar(value=1)
        self.reps_dropdown = tk.OptionMenu(
            self,
            self.reps_var,
            *[1, 2, 4, 6, 8, 10, 12],
            command=lambda val: new_hlc.set_number_of_reps(int(val))
        )
        self.reps_dropdown.pack(pady=10)

        self.run_btn = tk.Button(self, text="Run Exercise", command=new_hlc.perform_reps)
        self.run_btn.pack(pady=10)

        self.add_back_button(self, controller)

    def on_show(self):
        new_hlc.init_e_0()
        new_hlc.init_theta_0()


