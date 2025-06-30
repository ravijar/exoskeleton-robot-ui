import tkinter as tk
from ui.start_page import StartPage
from ui.exercise_selection_page import ExerciseSelectionPage
from ui.exercise_detail_page import ExerciseDetailPage
from ui.arduino_data_page import ArduinoDataPage

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
        for F in (StartPage, ExerciseSelectionPage, ExerciseDetailPage, ArduinoDataPage):
            page_name = F.__name__
            frame = F(self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

if __name__ == "__main__":
    app = ExoApp()
    app.mainloop()
