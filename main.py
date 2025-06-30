import tkinter as tk
from ui.start_page import StartPage
from ui.exercise_selection_page import ExerciseSelectionPage
from ui.exercise_detail_page import ExerciseDetailPage
from ui.arduino_data_page import ArduinoDataPage

class ExoApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Rehabilitation Exoskeleton")
        self.minsize(600, 500)  # Optional: prevent too small a window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Shared variables
        self.selected_exercise = tk.StringVar()
        self.selected_reps = tk.IntVar(value=1)
        self.output_angle = tk.DoubleVar(value=0.0)
        self.current_reps = tk.IntVar(value=0)

        self.frames = {}
        for F in (StartPage, ExerciseSelectionPage, ExerciseDetailPage, ArduinoDataPage):
            page_name = F.__name__
            frame = F(self)
            self.frames[page_name] = frame

            # Make all pages expandable to fill the window
            frame.grid(row=0, column=0, sticky="nsew")
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

if __name__ == "__main__":
    app = ExoApp()
    app.mainloop()
