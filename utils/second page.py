"""
currently unused, but it has a cutie gif so i keep it for later
"""


import threading


from tkinter import ttk, DISABLED, NORMAL
# class SecondPage(tk.Frame):
#     def __init__(self, controller: Controller):
#         tk.Frame.__init__(self, controller.container)
#         self.controller = controller
#         self.lbl = ImageLabel(self)
#         #self.dict_check_buttons = dict()
#         for item in controller.files:
#             self.controller.swap_dict[item] = tk.IntVar()
#         request_messege = tk.Label(self, text="Select  the \"swapped ratio\" files", font=MAIN_FONT,
#                                    fg="LightBlue4")
#         default_lable = tk.Label(self, text= "All unselected files get ratio = light/heavy", font=("David", 10), fg="LightBlue4")
#         request_messege.grid(column=0, row=0, pady=5, padx=10, columnspan=2)
#         default_lable.grid(column=0, row=1, columnspan=2)
#         assert(controller.number_of_files == len(controller.files))
#         for i in range(controller.number_of_files):
#             check_button = tk.Checkbutton(self, text=controller.files[i],
#                                           variable=self.controller.swap_dict[controller.files[i]],
#                                           font=("Arial", 9))
#             check_button.grid(column=0, row=i + 2, columnspan=2, sticky="W")
#
#         curr_row = controller.number_of_files + 2
#         back_button = ttk.Button(self, text="Back", command=lambda: controller.back_to_start_page())
#         back_button.grid(row=curr_row, column=0)
#         run_button = ttk.Button(self, text="Run",
#                                 command=lambda: self._progress_bar(run_button, back_button, curr_row))
#         run_button.grid(row=curr_row, column=1, padx=10, pady=10)
#
#
#
#
#     def _progress_bar(self, run: ttk.Button, back: ttk.Button, curr_row):
#         run.configure(state=DISABLED)
#         back.configure(state=DISABLED)
#         self.lbl.grid(column=0, row=curr_row + 1, columnspan=2)
#         self.lbl.load('phage.gif')
#         precent = tk.Label(self, text="Running...please wait", font=("David", 10),
#                                  fg="LightBlue4")
#         precent.grid(column=0, row=curr_row+2, columnspan=2)
#         running_thread = threading.Thread(target=self.controller.run)
#         running_thread.start()





# def utility_func(i):
#     for k in range(i):
#         print(k)
#     exit(2)



# class ImageLabel(tk.Label):
#     """a label that displays images, and plays them if they are gifs"""
#     def load(self, im):
#         if isinstance(im, str):
#             im = Image.open(im)
#         self.loc = 0
#         self.frames = []
#
#         try:
#             for i in count(1):
#                 self.frames.append(ImageTk.PhotoImage(im.copy()))
#                 im.seek(i)
#         except EOFError:
#             pass
#
#         try:
#             self.delay = im.info['duration']
#         except:
#             self.delay = 100
#
#         if len(self.frames) == 1:
#             self.config(image=self.frames[0])
#         else:
#             self.next_frame()
#
#     def unload(self):
#         self.config(image=None)
#         self.frames = None
#
#     def next_frame(self):
#         if self.frames:
#             self.loc += 1
#             self.loc %= len(self.frames)
#             self.config(image=self.frames[self.loc])
#             self.after(self.delay, self.next_frame)

