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

import os

import logging
logger = logging.getLogger(__name__)

class ReorientationWindow:

    def __init__(self, parent):

        self.parent = parent
        self.reoriented_files = []

    def show(self):

        self.top = tk.Toplevel(self.parent)
        self.top.title('Convert Dicom Files')
        self.top.geometry('600x340')
        self.top.update()
        self.top.minsize(self.top.winfo_width(), self.top.winfo_height())
        self.top.resizable(False, False)
        self.top.focus_set()
        self.top.grab_set()

        self.top.attributes("-topmost", True)

        filesFrame = ttk.Labelframe(self.top, text='File Paths')
        filesFrame.grid(row=0, padx=5, pady=5, sticky="news")

        self.listbox_paths = tk.Listbox(filesFrame)
        self.listbox_paths.grid(row=1, columnspan=1, padx=(5,0), pady=5, sticky='news')

        # Add the files from the previous steps
        try:
            for f in self.parent.convert_dicom_window.converted_files:
                self.listbox_paths.insert(tk.END, f)
        except:
            # User hasn't run previous step
            pass

        vsb = ttk.Scrollbar(filesFrame, orient="vertical", command=self.listbox_paths.yview)
        vsb.grid(row=1, column=2, sticky=("N", "S", "E", "W"), padx=(0,10), pady=(5, 5))
        self.listbox_paths.configure(yscrollcommand=vsb.set)

        filesFrame.columnconfigure(0, weight=1)

        tk.Button(filesFrame,text='Add File', command=self.add_file, width=20).grid(row=0, padx=5, pady=5)
        tk.Button(filesFrame,text='Remove Selected', command=self.remove_file, width=20).grid(row=2, padx=5, pady=5)
        tk.Button(self.top,text='Run Reorientation', command=self.run, width=30, height=2).grid(row=2, padx=5, pady=5)

        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(6, weight=1)

    def add_file(self):

        self.file = os.path.normpath(filedialog.askopenfilename(parent=self.top))
        self.listbox_paths.insert(tk.END, self.file)

    def remove_file(self):

        selected_indexes = self.listbox_paths.curselection()

        for ind in selected_indexes:
            self.listbox_paths.delete(int(ind))

    def run(self):

        print(self.listbox_paths.get(0,tk.END))
