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

        # Labelframe with style for font
        s = ttk.Style()
        s.configure('Main.TLabelframe.Label', font=('helvetica', 12, 'bold'))
        filesFrame = ttk.Labelframe(self.top, text='File Paths', style = "Main.TLabelframe")
        filesFrame.grid(row=0, padx=5, pady=5, sticky="news")
        filesFrame.rowconfigure(2, weight=1)
        filesFrame.columnconfigure(0, weight=1)

        # Description Message
        tk.Message(filesFrame, text="Description goes here", font=("Helvetica", 10), width=500, justify=tk.CENTER).grid(row=0, column=0, padx=1, pady=2, sticky='ew')
        
        # Add file button
        tk.Button(filesFrame,text='Add File', command=self.add_file, width=20).grid(row=1, padx=5, pady=5)

        # Main  list box
        self.listbox_paths = tk.Listbox(filesFrame)
        self.listbox_paths.grid(row=2, columnspan=1, padx=(5,0), pady=5, sticky='news')

        # Add the files from the previous steps to the listbox
        try:
            for f in self.parent.convert_dicom_window.converted_files:
                self.listbox_paths.insert(tk.END, f)
        except:
            # User hasn't run previous step
            pass

        # Scrollbar for list box
        vsb = ttk.Scrollbar(filesFrame, orient="vertical", command=self.listbox_paths.yview)
        vsb.grid(row=2, column=2, sticky=("N", "S", "E", "W"), padx=(0,10), pady=(5, 5))
        self.listbox_paths.configure(yscrollcommand=vsb.set)

        # Remove selected button
        tk.Button(filesFrame,text='Remove Selected', command=self.remove_file, width=20).grid(row=3, padx=5, pady=5)
        
        # Reorient button
        tk.Button(self.top,text='Reorient', command=self.reorient, width=30, height=2).grid(row=2, padx=5, pady=5)

        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(0, weight=1)

    def add_file(self):

        initial_dir = self.parent.workspace
        
        if self.listbox_paths.size() > 0:
            initial_dir = os.path.dirname(self.listbox_paths.get(tk.END))
            
        f = filedialog.askopenfilename(parent=self.top, initialdir=initial_dir)
        if len(f) == 0:
            # Cancelled
            return
        f = os.path.normpath(f)
        
        self.listbox_paths.insert(tk.END, f)

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

        self.reoriented_files = []
        for input_file in input_files:
            output_file = reorient(input_file,output_dir)
            self.reoriented_files.append(output_file)

        messagebox.showinfo("Done", "Reorientation Completed", parent=self.top)

        self.top.destroy()
