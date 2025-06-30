import tkinter as tk

class StartPage(tk.Frame):
    def __init__(self, controller):
        super().__init__(controller)
        tk.Label(self, text="Rehabilitation Exoskeleton", font=("Arial", 18)).pack(pady=60)
        tk.Button(self, text="Start", command=lambda: controller.show_frame("ExerciseSelectionPage")).pack(pady=20)
        tk.Button(self, text="Arduino Data Page", command=lambda: controller.show_frame("ArduinoDataPage")).pack(pady=10)

