from tkinter import ttk
import tkinter as tk
from xml_parser_view import Controller, MAIN_FONT


class SecondPage(tk.Frame):
    def __init__(self, controller: Controller):
        tk.Frame.__init__(self, controller.container)
        self.controller = controller
        for item in controller.files:
            self.controller.swap_dict[item] = tk.IntVar()

        request_messege = tk.Label(self, text="Select  the \"swapped ratio\" files", font=MAIN_FONT,fg="LightBlue4")
        default_lable = tk.Label(self, text= "All unselected files get ratio = light/heavy", font=("David", 10), fg="LightBlue4")
        request_messege.grid(column=0, row=0, pady=5, padx=10, columnspan=2)
        default_lable.grid(column=0, row=1, columnspan=2)
        assert(controller.number_of_files == len(controller.files))
        for i in range(controller.number_of_files):
             check_button = tk.Checkbutton(self, text=controller.files[i],
                                           variable=self.controller.swap_dict[controller.files[i]],
                                           font=("Arial", 9))
             check_button.grid(column=0, row=i + 2, columnspan=2, sticky="W")

        curr_row = controller.number_of_files + 2
        back_button = ttk.Button(self, text="Back", command=lambda: controller.back_to_start_page())
        back_button.grid(row=curr_row, column=0)
        run_button = ttk.Button(self, text="Run",
                                 command=lambda: self._progress_bar(run_button, back_button, curr_row))
        run_button.grid(row=curr_row, column=1, padx=10, pady=10)