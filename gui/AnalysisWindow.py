#!/usr/bin/env python3
try:
    # Python 2
    import Tkinter  as tk
    import ttk
    import tkMessageBox as messagebox
    import tkFileDialog as filedialog
    import tkSimpleDialog as simpledialog
except ImportError:
    # Python 3
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox
    from tkinter import filedialog
    from tkinter import simpledialog

import os

import logging
logger = logging.getLogger(__name__)

from analysis.distortion import perform_analysis

class AnalysisWindow:

    def __init__(self, parent):

        self.parent = parent
        #self.deformed_files = []

    def show(self):

        self.top = tk.Toplevel(self.parent)
        self.top.title('Analysis')
        self.top.geometry('600x600')
        self.top.update()
        self.top.minsize(self.top.winfo_width(), self.top.winfo_height())
        self.top.resizable(True, True)
        self.top.focus_set()
        self.top.grab_set()

        self.top.attributes("-topmost", True)

        self.source_file = tk.StringVar()
        source_frame = ttk.Labelframe(self.top, text='Registration CSV File')
        source_frame.grid(row=0, padx=15, pady=15, sticky="ew")
        tk.Label(source_frame,textvariable=self.source_file, font=("Helvetica", 10)).grid(row=1, padx=15, pady=15)
        tk.Button(source_frame,text='Choose Registration CSV File', command=self.choose_source_file).grid(row=2, padx=5, pady=5)

        tk.Button(self.top,text='Analyse', command=self.analyse, width=30, height=2).grid(row=4, padx=5, pady=5)

        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(5, weight=1)

    def choose_source_file(self):
        file = filedialog.askopenfilename(parent=self.top, initialdir=self.source_file.get())
        if not type(file)==str or len(file) == 0:
            # Dialog cancelled
            return
        self.source_file.set(os.path.normpath(file))

    def analyse(self):

        # Create the output directory if it doesn't already exist
        output_dir = os.path.join(self.parent.workspace,'step6')
        try:
            # Python 3
            os.makedirs(output_dir, exist_ok=True) # > Python 3.2
        except TypeError:
            # Python 2
            try:
                os.makedirs(output_dir)
            except OSError:
                if not os.path.isdir(output_dir):
                    raise

        perform_analysis(self.source_file.get())

        messagebox.showinfo("Done", "Analysis Completed")

        self.top.destroy()
