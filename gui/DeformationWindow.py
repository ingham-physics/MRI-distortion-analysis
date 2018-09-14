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

from MRL_deformable.mrl_deformable import mrl_deformable

class DeformationWindow:

    def __init__(self, parent):

        self.parent = parent
        self.deformed_files = []

    def show(self):

        self.top = tk.Toplevel(self.parent)
        self.top.title('Deformation')
        self.top.geometry('600x600')
        self.top.update()
        self.top.minsize(self.top.winfo_width(), self.top.winfo_height())
        self.top.resizable(True, True)
        self.top.focus_set()
        self.top.grab_set()

        self.top.attributes("-topmost", True)

        self.source_file = tk.StringVar()
        source_frame = ttk.Labelframe(self.top, text='Source File')
        source_frame.grid(row=0, padx=15, pady=15, sticky="ew")
        tk.Label(source_frame,textvariable=self.source_file, font=("Helvetica", 10)).grid(row=1, padx=15, pady=15)
        tk.Button(source_frame,text='Choose Source File', command=self.choose_source_file).grid(row=2, padx=5, pady=5)

        self.target_file = tk.StringVar()
        target_frame = ttk.Labelframe(self.top, text='Target File')
        target_frame.grid(row=1, padx=15, pady=15, sticky="ew")
        tk.Label(target_frame,textvariable=self.target_file, font=("Helvetica", 10)).grid(row=1, padx=15, pady=15)
        tk.Button(target_frame,text='Choose Target File', command=self.choose_target_file).grid(row=2, padx=5, pady=5)

        self.grid_spacing = tk.StringVar()
        self.grid_spacing.set("25")
        grid_spacing_frame = ttk.Labelframe(self.top, text='Grid Spacing (mm)')
        grid_spacing_frame.grid(row=2, padx=15, pady=15, sticky="ew")
        tk.Label(grid_spacing_frame,textvariable=self.grid_spacing, font=("Helvetica", 10)).grid(row=1, padx=15, pady=15)
        tk.Button(grid_spacing_frame,text='Change Grid Spacing', command=self.change_grid_spacing).grid(row=2, padx=5, pady=5)

        self.threshold = tk.StringVar()
        self.threshold.set("100")
        threshold_frame = ttk.Labelframe(self.top, text='Threshold')
        threshold_frame.grid(row=3, padx=15, pady=15, sticky="ew")
        tk.Label(threshold_frame,textvariable=self.threshold, font=("Helvetica", 10)).grid(row=1, padx=15, pady=15)
        tk.Button(threshold_frame,text='Change Threshold', command=self.change_threshold).grid(row=2, padx=5, pady=5)

        tk.Button(self.top,text='Deform', command=self.deform, width=30, height=2).grid(row=4, padx=5, pady=5)

        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(5, weight=1)

    def choose_source_file(self):
        file = filedialog.askopenfilename(parent=self.top, initialdir=self.source_file.get())
        if not type(file)==str or len(file) == 0:
            # Dialog cancelled
            return
        self.source_file.set(os.path.normpath(file))

    def choose_target_file(self):
        file = filedialog.askopenfilename(parent=self.top, initialdir=self.target_file.get())
        if not type(file)==str or len(file) == 0:
            # Dialog cancelled
            return
        self.target_file.set(os.path.normpath(file))

    def change_grid_spacing(self):
        
        gs = simpledialog.askinteger("Grid Spacing", "Enter the spline grid spacing in mm",
                                 parent=self.top,
                                 minvalue=0, maxvalue=100,
                                 initialvalue=int(self.grid_spacing.get())
                                 )

        if gs == None:
            # Dialog cancelled
            return
        self.grid_spacing.set(str(gs))

    def change_threshold(self):
        
        th = simpledialog.askinteger("Threshold", "Enter the threshold",
                                 parent=self.top,
                                 minvalue=0, maxvalue=1000,
                                 initialvalue=int(self.threshold.get())
                                 )

        if th == None:
            # Dialog cancelled
            return
        self.threshold.set(str(th))

    def deform(self):

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

        csv_file, def_file = mrl_deformable(self.source_file.get(),self.target_file.get(), output_dir, int(self.grid_spacing.get()), int(self.threshold.get()))
        self.deformed_files.append(csv_file)
        self.deformed_files.append(def_file)

        messagebox.showinfo("Done", "Deformation Completed", parent=self.top)

        self.top.destroy()
