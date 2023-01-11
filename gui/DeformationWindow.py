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

    def __init__(self, parent, previous):

        self.parent = parent
        self.title = 'Deformable Registration'
        self.previous = previous
        self.output = []

    def show(self):

        self.top = tk.Toplevel(self.parent)
        self.top.title('Deformation')

        # Define width and height of this window
        w = 600
        h = 800

        # Place the window in the centre of the screen
        ws = self.parent.winfo_screenwidth()
        hs = self.parent.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.top.geometry('%dx%d+%d+%d' % (w, h, x, y))

        self.top.update()
        self.top.minsize(self.top.winfo_width(), self.top.winfo_height())
        self.top.resizable(True, True)
        self.top.focus_set()
        self.top.grab_set()

        # StringVars for source and target and params
        self.source_file = tk.StringVar()
        self.target_file = tk.StringVar()
        self.grid_spacing = tk.StringVar()
        self.grid_spacing.set("25")
        self.threshold = tk.StringVar()
        self.threshold.set("300")
        
        # Define style for labelframe
        s = ttk.Style()
        s.configure('Main.TLabelframe.Label', font=('helvetica', 12, 'bold'))

        # Source labelframe
        source_frame = ttk.Labelframe(self.top, text='Source File', style = "Main.TLabelframe")
        source_frame.grid(row=0, padx=15, pady=15, sticky="ew")
        source_frame.columnconfigure(0, weight=1)

        # Message for source
        tk.Message(source_frame, text="Select the moving image to be deformed to the target image", font=("Helvetica", 10), width=500, justify=tk.CENTER).grid(row=0, column=0, padx=1, pady=2, sticky='ew')

        # Source file label
        tk.Label(source_frame,textvariable=self.source_file, font=("Helvetica", 10, 'bold')).grid(row=2, padx=15, pady=15)

        # Choose source button
        tk.Button(source_frame,text='Choose Source File', command=self.choose_source_file).grid(row=3, padx=5, pady=5)

        # If there is output from the previous step, load the first file as the source file
        if self.previous:
            if len(self.previous.output) > 0: self.source_file.set(self.previous.output[0])

        # Target labelframe
        target_frame = ttk.Labelframe(self.top, text='Target File', style = "Main.TLabelframe")
        target_frame.grid(row=1, padx=15, pady=15, sticky="ew")
        target_frame.columnconfigure(0, weight=1)

        # Message for target
        tk.Message(target_frame, text="Select the fixed target image for the deformable registration", font=("Helvetica", 10), width=500, justify=tk.CENTER).grid(row=0, column=0, padx=1, pady=2, sticky='ew')

        # Target file label
        tk.Label(target_frame,textvariable=self.target_file, font=("Helvetica", 10,'bold')).grid(row=1, padx=15, pady=15)

        # Choose target button
        tk.Button(target_frame,text='Choose Target File', command=self.choose_target_file).grid(row=2, padx=5, pady=5)

        # If there is output from the previous step, load the second file as the target file
        if self.previous:
            if len(self.previous.output) > 1: self.target_file.set(self.previous.output[1])

        # Grid spacing labelframe
        grid_spacing_frame = ttk.Labelframe(self.top, text='Grid Spacing (mm)', style = "Main.TLabelframe")
        grid_spacing_frame.grid(row=2, padx=15, pady=15, sticky="ew")
        grid_spacing_frame.columnconfigure(0, weight=1)

        # Message for grid spacing
        tk.Message(grid_spacing_frame, text="Final control point grid spacing for the registration. Recommended values: 25mm for Phantoms; 10mm for anatomical images. Avoid making grid too small to ensure smooth DVF.", font=("Helvetica", 10), width=500, justify=tk.CENTER).grid(row=0, column=0, padx=1, pady=2, sticky='ew')

        # Grid spacing label
        tk.Label(grid_spacing_frame,textvariable=self.grid_spacing, font=("Helvetica", 10, 'bold')).grid(row=1, padx=15, pady=15)

        # Change grid spacing button
        tk.Button(grid_spacing_frame,text='Change Grid Spacing', command=self.change_grid_spacing).grid(row=2, padx=5, pady=5)

        # Threshold labelframe
        threshold_frame = ttk.Labelframe(self.top, text='Threshold', style = "Main.TLabelframe")
        threshold_frame.grid(row=3, padx=15, pady=15, sticky="ew")
        threshold_frame.columnconfigure(0, weight=1)

        # Message for threshold
        tk.Message(threshold_frame, text="Select a threshold intensity to be used to mask the deformation field for the following analysis (based on intensities of image being deformed)", font=("Helvetica", 10), width=500, justify=tk.CENTER).grid(row=0, column=0, padx=1, pady=2, sticky='ew')

        # Change threshold label
        tk.Label(threshold_frame,textvariable=self.threshold, font=("Helvetica", 10, 'bold')).grid(row=1, padx=15, pady=15)

        # Change threshold button
        tk.Button(threshold_frame,text='Change Threshold', command=self.change_threshold).grid(row=2, padx=5, pady=5)

        tk.Button(self.top,text='Deform', command=self.deform, width=30, height=2).grid(row=4, padx=5, pady=5)

        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(5, weight=1)

        # This is a modal window so wait until it is closed
        self.top.wait_window()

    def choose_source_file(self):
        initial_dir = os.path.dirname(self.source_file.get())
        if len(initial_dir) == 0:
            initial_dir = self.parent.workspace
        file = filedialog.askopenfilename(parent=self.top, initialdir=initial_dir)
        if not type(file)==str or len(file) == 0:
            # Dialog cancelled
            return
        self.source_file.set(os.path.normpath(file))

    def choose_target_file(self):
        initial_dir = os.path.dirname(self.target_file.get())
        if len(initial_dir) == 0:
            initial_dir = self.parent.workspace
        file = filedialog.askopenfilename(parent=self.top, initialdir=initial_dir)
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
        output_dir = os.path.join(self.parent.workspace,'deform')
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

        self.output = []
        csv_file, def_file = mrl_deformable(self.source_file.get(),self.target_file.get(), output_dir, int(self.grid_spacing.get()), int(self.threshold.get()))
        self.output.append(csv_file)
        self.output.append(def_file)

        messagebox.showinfo("Done", "Deformation Completed", parent=self.top)

        self.top.destroy()
