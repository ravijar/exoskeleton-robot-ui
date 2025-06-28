import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import serial

# --- Serial Setup ---
PICO_PORT = "COM14"
BAUD_RATE = 115200

try:
    ser = serial.Serial(PICO_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
except Exception as e:
    ser = None
    print("Serial connection failed:", e)

def send_to_pico(command):
    if ser and ser.is_open:
        try:
            ser.write((command + "\n").encode())
        except Exception as e:
            print("Failed to send command:", e)

# --- Tkinter App ---
class ExoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rehabilitation Exoskeleton")
        self.geometry("500x400")
        self.selected_exercise = tk.StringVar()
        self.selected_reps = tk.IntVar(value=1)
        self.output_angle = tk.DoubleVar(value=0.0)
        self.current_reps = tk.IntVar(value=0)

        self.frames = {}
        for F in (StartPage, ExerciseSelectionPage, ExerciseDetailPage):
            page_name = F.__name__
            frame = F(self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

class StartPage(tk.Frame):
    def __init__(self, controller):
        super().__init__(controller)
        tk.Label(self, text="Rehabilitation Exoskeleton", font=("Arial", 18)).pack(pady=60)
        tk.Button(self, text="Start", command=lambda: controller.show_frame("ExerciseSelectionPage")).pack(pady=20)

class ExerciseSelectionPage(tk.Frame):
    def __init__(self, controller):
        super().__init__(controller)
        tk.Label(self, text="Choose the exercise", font=("Arial", 16)).pack(pady=20)

        exercises = [("Leg Curls", "Leg Curls improve hamstring strength."),
                     ("Leg Extensions", "Leg Extensions focus on quadriceps."),
                     ("Cycling", "Cycling boosts overall knee mobility.")]

        for name, desc in exercises:
            tk.Button(self, text=name, width=20,
                      command=lambda n=name, d=desc: self.select_exercise(controller, n, d)).pack(pady=5)

    def select_exercise(self, controller, name, desc):
        controller.selected_exercise.set(name)
        controller.frames["ExerciseDetailPage"].set_description(desc)
        controller.show_frame("ExerciseDetailPage")

class ExerciseDetailPage(tk.Frame):
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

        self.reps_label = tk.Label(self, text="Current Reps: 0", font=("Arial", 12))
        self.reps_label.pack(pady=10)

        self.continue_btn = tk.Button(self, text="Continue", command=self.reset_for_next_round)
        self.continue_btn.pack(pady=10)
        self.continue_btn.pack_forget()  # initially hidden

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
        send_to_pico("ON")  # LED ON when initialization starts
        threading.Thread(target=self._simulate_initialization).start()

    def _simulate_initialization(self):
        for i in range(101):
            time.sleep(0.02)
            self.progress["value"] = i
        self.tick_label.config(text="✓")
        self.controller.output_angle.set(round(45 + 10 * time.time() % 5, 2))
        self.angle_label.config(text=f"Output Angle: {self.controller.output_angle.get()}°")
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
        send_to_pico("OFF")  # LED OFF after round

if __name__ == "__main__":
    app = ExoApp()
    app.mainloop()
