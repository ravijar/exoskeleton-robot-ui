import tkinter as tk

class BackButtonMixin:
    def add_back_button(self, parent, controller, back_page="StartPage"):
        back_btn = tk.Button(parent, text="← Back", command=lambda: controller.show_frame(back_page))
        back_btn.pack(pady=10, anchor="w")
