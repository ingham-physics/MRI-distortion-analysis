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
        self.top.geometry('600x340')
        self.top.update()
        self.top.minsize(self.top.winfo_width(), self.top.winfo_height())
        self.top.resizable(True, True)
        self.top.focus_set()
        self.top.grab_set()

        self.top.attributes("-topmost", True)

        filesFrame = ttk.Labelframe(self.top, text='Dicom Paths')
        filesFrame.grid(row=0, padx=5, pady=5, sticky="news")
        filesFrame.rowconfigure(2, weight=1)

        self.listbox_paths = tk.Listbox(filesFrame)
        self.listbox_paths.grid(row=2, columnspan=1, padx=(5,0), pady=5, sticky='news')

        vsb = ttk.Scrollbar(filesFrame, orient="vertical", command=self.listbox_paths.yview)
        vsb.grid(row=2, column=2, sticky=("N", "S", "E", "W"), padx=(0,10), pady=(5, 5))
        self.listbox_paths.configure(yscrollcommand=vsb.set)

        filesFrame.columnconfigure(0, weight=1)

        tk.Label(filesFrame, text="Description label", font=("Helvetica", 10)).grid(row=0, padx=10, pady=10)

        tk.Button(filesFrame,text='Add Dicom Series', command=self.add_file, width=20).grid(row=1, padx=5, pady=5)
        tk.Button(filesFrame,text='Remove Selected', command=self.remove_file, width=20).grid(row=3, padx=5, pady=5)
        tk.Button(self.top,text='Convert', command=self.convert, width=30, height=2).grid(row=2, padx=5, pady=5)

        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(0, weight=1)

    def add_file(self):

        self.file = os.path.normpath(filedialog.askdirectory(parent=self.top))
        self.listbox_paths.insert(tk.END, self.file)

    def remove_file(self):

        selected_indexes = self.listbox_paths.curselection()

        for ind in selected_indexes:
            self.listbox_paths.delete(int(ind))

    def convert(self):

        dicom_paths = self.listbox_paths.get(0,tk.END)

        # Make sure the user has selected at least one directory
        if len(dicom_paths) == 0:
            messagebox.showerror("Select Directory", "Add at least one directory containing the Dicom files to convert.", parent=self.top)
            return

        # Create the output directory if it doesn't already exist
        output_dir = os.path.join(self.parent.workspace,'step1')
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

        files_converted_success = True

        ind = 0
        for input_dir in dicom_paths:
        
            # Use the directory name as a file name
            output_file = os.path.basename(input_dir) + '.nii.gz'
            output_file = os.path.join(output_dir,output_file)
            output_file = os.path.join(os.getcwd(),output_file)

            try:
                result = subprocess.check_output(["itkDicomSeriesReadImageWrite", input_dir, output_file])
                logger.info("Files converted from " + input_dir + " written to " + output_file)
                self.converted_files.append(output_file)
                self.listbox_paths.delete(int(ind))
                
            except:
                logger.warn("Error converting files from " + input_dir + " to " + output_file)
                files_converted_success = False
                ind = ind + 1
        
        # Finally show a message describing which files were successfully converted
        if files_converted_success:
            messagebox.showinfo("Success", "Files converted successfully", parent=self.top)

            # Close the window
            self.top.destroy()
        else:
            messagebox.showerror("Error", "Unable to convert some files. Ensure that paths contain Dicom series.", parent=self.top)
