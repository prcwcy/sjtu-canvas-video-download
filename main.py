import tkinter as tk
from sjtu_canvas_video_main_frame import MainFrame

root = tk.Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
MainFrame(root)
root.mainloop()
