import tkinter as tk
from tkinter import ttk
import threading
import time
from service.serial_comm import send_to_pico, read_response
from ui.back_button_mixin import BackButtonMixin

class ExerciseDetailPage(tk.Frame, BackButtonMixin):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller

        self.description = tk.Label(self, text="", wraplength=200, anchor='ne', justify='right')
        self.description.place(x=300, y=10, width=180)

        tk.Label(self, text="Select Number of Reps", font=("Arial", 14)).pack(pady=(30, 5))
        reps_dropdown = ttk.Combobox(self, values=[1, 2, 4, 6, 8, 10, 12],
                                     textvariable=controller.selected_reps, state="readonly")
        reps_dropdown.pack(pady=5)

        tk.Label(self, text="Initialize the angle", font=("Arial", 14)).pack(pady=(20, 5))
        init_frame = tk.Frame(self)
        init_frame.pack()

        self.init_button = tk.Button(init_frame, text="Initialize Angle", command=self.start_initialization)
        self.init_button.pack(side=tk.LEFT)

        self.tick_label = tk.Label(init_frame, text="", font=("Arial", 16))
        self.tick_label.pack(side=tk.LEFT, padx=10)

        self.progress = ttk.Progressbar(self, orient="horizontal", mode="determinate", length=200)
        self.progress.pack(pady=10)
        self.progress["value"] = 0

        self.angle_label = tk.Label(self, text="")
        self.angle_label.pack()

        self.mpu_label = tk.Label(self, text="MPU Data: Not available", font=("Arial", 10))
        self.mpu_label.pack(pady=5)

        self.reps_label = tk.Label(self, text="Current Reps: 0", font=("Arial", 12))
        self.reps_label.pack(pady=10)

        self.continue_btn = tk.Button(self, text="Continue", command=self.reset_for_next_round)
        self.continue_btn.pack(pady=10)
        self.continue_btn.pack_forget()

        self.add_back_button(self, controller)

    def set_description(self, desc):
        self.description.config(text=desc)
        self.controller.output_angle.set(0.0)
        self.controller.current_reps.set(0)
        self.update_reps_display()
        self.progress["value"] = 0
        self.tick_label.config(text="")
        self.angle_label.config(text="")
        self.continue_btn.pack_forget()

    def start_initialization(self):
        self.init_button.config(state='disabled')
        send_to_pico("ON")
        threading.Thread(target=self._simulate_initialization).start()

    def _simulate_initialization(self):
        for i in range(101):
            time.sleep(0.02)
            self.progress["value"] = i

        # Request MPU6050 data
        send_to_pico("READ")
        time.sleep(0.1)
        mpu_data = read_response()

        self.tick_label.config(text="✓")
        self.controller.output_angle.set(round(45 + 10 * time.time() % 5, 2))
        self.angle_label.config(text=f"Output Angle: {self.controller.output_angle.get()}°")
        
        # Display MPU data
        if mpu_data:
            try:
                ax, ay, az, gx, gy, gz = map(float, mpu_data.split(","))
                self.mpu_label.config(text=f"ACC: {ax:.2f}, {ay:.2f}, {az:.2f} | GYRO: {gx:.2f}, {gy:.2f}, {gz:.2f}")
            except:
                self.mpu_label.config(text="MPU Data: Error parsing")
        else:
            self.mpu_label.config(text="MPU Data: No response")

        self.controller.current_reps.set(1)
        self.update_reps_display()
        self.check_reps()

    def update_reps_display(self):
        current = self.controller.current_reps.get()
        self.reps_label.config(text=f"Current Reps: {current}")

    def check_reps(self):
        if self.controller.current_reps.get() >= self.controller.selected_reps.get():
            self.continue_btn.pack()

    def reset_for_next_round(self):
        current = self.controller.current_reps.get()
        self.controller.current_reps.set(current + 1)
        self.update_reps_display()
        self.tick_label.config(text="")
        self.progress["value"] = 0
        self.init_button.config(state='normal')
        self.continue_btn.pack_forget()
        send_to_pico("OFF")
