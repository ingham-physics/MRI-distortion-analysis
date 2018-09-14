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

from ReOrientation.orientation import reorient

class ReorientationWindow:

    def __init__(self, parent):

        self.parent = parent
        self.reoriented_files = []

    def show(self):

        self.top = tk.Toplevel(self.parent)
        self.top.title('Reorientation')
        self.top.geometry('600x340')
        self.top.update()
        self.top.minsize(self.top.winfo_width(), self.top.winfo_height())
        self.top.resizable(True, True)
        self.top.focus_set()
        self.top.grab_set()

        self.top.attributes("-topmost", True)

        filesFrame = ttk.Labelframe(self.top, text='File Paths')
        filesFrame.grid(row=0, padx=5, pady=5, sticky="news")
        filesFrame.rowconfigure(1, weight=1)

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
        tk.Button(self.top,text='Reorient', command=self.reorient, width=30, height=2).grid(row=2, padx=5, pady=5)

        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(0, weight=1)

    def add_file(self):

        self.file = os.path.normpath(filedialog.askopenfilename(parent=self.top))
        self.listbox_paths.insert(tk.END, self.file)

    def remove_file(self):

        selected_indexes = self.listbox_paths.curselection()

        for ind in selected_indexes:
            self.listbox_paths.delete(int(ind))

    def reorient(self):

        input_files = self.listbox_paths.get(0,tk.END)

        if len(input_files) > 0:

            # Create the output directory if it doesn't already exist
            output_dir = os.path.join(self.parent.workspace,'step2')
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

        for input_file in input_files:
            output_file = reorient(input_file,output_dir)
            self.reoriented_files.append(output_file)

        messagebox.showinfo("Done", "Reorientation Completed", parent=self.top)

        self.top.destroy()
