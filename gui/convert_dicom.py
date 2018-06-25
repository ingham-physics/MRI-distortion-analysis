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

class ConvertDicomWindow:

    def __init__(self, parent):

        self.parent = parent
        self.converted_files = []

    def show(self):

        self.top = tk.Toplevel(self.parent)
        self.top.title('Convert Dicom Files')
        self.top.geometry('480x140')
        self.top.update()
        self.top.minsize(self.top.winfo_width(), self.top.winfo_height())
        self.top.resizable(False, False)
        self.top.focus_set()
        self.top.grab_set()

        self.top.attributes("-topmost", True)

        self.top.columnconfigure(0, weight=10)
        self.top.columnconfigure(1, weight=1)

        tk.Label(self.top, text='Select directory:').grid(row=0, columnspan=2, padx=5, pady=5)

        self.txt_path = tk.Entry(self.top)

        self.txt_path.grid(row=1, column=0, padx=5, pady=5, sticky='NEWS')

        tk.Button(self.top,text='...',command=self.select_path).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.top,text='Convert',command=self.convert, width=15).grid(row=3, columnspan=2, padx=5, pady=5)

        self.parent.wait_window(self.top)

    # Select a path and enter it in the text box
    def select_path(self):

        self.directory = filedialog.askdirectory(parent=self.top)
        self.txt_path.delete(0,tk.END)
        self.txt_path.insert(0,self.directory)

    def convert(self):

        input_dir = self.txt_path.get()

        # Make sure they selected a directory
        if not input_dir:
            messagebox.showerror("Select Directory", "Select the directory containing the Dicom files to convert.")
            return

        # Create the output directory if it doesn't already exist
        output_dir = 'working/step1'
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

        # Use the directory name as a file name
        output_file = os.path.basename(input_dir) + '.nii.gz'
        output_file = os.path.join(output_dir,output_file)
        output_file = os.path.join(os.getcwd(),output_file)

        try:
            result = subprocess.check_output(["itkDicomSeriesReadImageWrite", input_dir, output_file])
            logger.info("Files converted from " + input_dir + " written to " + output_file)
            self.converted_files.append(output_file)
            messagebox.showinfo("Success", "Files converted successfully and written to: " + output_file)
        except:
            messagebox.showerror("Error", "Unable to convert files. Ensure that the correct directory is selected.")
            logger.warn("Error converting files from " + input_dir + " to " + output_file)
