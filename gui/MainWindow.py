#!/usr/bin/env python3
try:
    # Python 2
    import Tkinter  as tk
    import ttk
    import tkMessageBox as messagebox
    import tkFileDialog as filedialog
except ImportError:
    # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox
    from tkinter import filedialog

import os, subprocess

import logging
logger = logging.getLogger(__name__)

class MainWindow:

    def __init__(self, parent):

        self.parent = parent
        self.converted_files = []

    def show(self, title, msg, workflow_steps):

        self.top = tk.Toplevel(self.parent)
        self.top.title(title)

        # Define width and height of this window
        w = 400
        h = 550

        # Place the window in the centre of the screen
        ws = self.parent.winfo_screenwidth()
        hs = self.parent.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.top.geometry('%dx%d+%d+%d' % (w, h, x, y))

        self.top.update()
        self.top.minsize(self.top.winfo_width(), self.top.winfo_height())
        self.top.resizable(True, True)
        self.top.takefocus = True
        self.top.focus_set()
        self.top.grab_set()

        # Label for workflow title
        tk.Label(self.top, text=title, font=("Helvetica", 16)).grid(row=0, padx=10, pady=10)

        # Message for workflow
        tk.Message(self.top, text=msg, font=("Helvetica", 10), width=500, justify=tk.CENTER).grid(row=1, column=0, padx=1, pady=2, sticky='ew')

        # Buttons to launch workflow
        step_number = 1
        for step in workflow_steps:
            tk.Button(self.top,text='Step {0}: {1}'.format(step_number, step.title), 
                command= lambda s=step: self.show_window(s),
                font=("Helvetica", 10, 'bold'),
                width=30, 
                height=2).grid(row=step_number+5, padx=10, pady=10)
            step_number += 1

        self.top.columnconfigure(0, weight=1)

        self.top.wait_window()

    def show_window(self, window):

        self.top.withdraw()
        window.show()
        self.top.deiconify()
