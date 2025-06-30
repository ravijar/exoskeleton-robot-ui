import tkinter as tk
from ui.back_button_mixin import BackButtonMixin

class ExerciseSelectionPage(tk.Frame, BackButtonMixin):
    def __init__(self, controller):
        super().__init__(controller)
        tk.Label(self, text="Choose the exercise", font=("Arial", 16)).pack(pady=20)

        exercises = [("Leg Curls", "Leg Curls improve hamstring strength."),
                     ("Leg Extensions", "Leg Extensions focus on quadriceps."),
                     ("Cycling", "Cycling boosts overall knee mobility.")]

        for name, desc in exercises:
            tk.Button(self, text=name, width=20,
                      command=lambda n=name, d=desc: self.select_exercise(controller, n, d)).pack(pady=5)
            
        self.add_back_button(self, controller)

    def select_exercise(self, controller, name, desc):
        controller.selected_exercise.set(name)
        controller.frames["ExerciseDetailPage"].set_description(desc)
        controller.show_frame("ExerciseDetailPage")
