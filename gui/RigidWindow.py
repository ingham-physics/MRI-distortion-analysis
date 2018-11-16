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

from rigid.rigid import rigid

class RigidWindow:

    def __init__(self, parent):

        self.parent = parent
        self.title = 'Rigid Registration'
        self.registered_files = []

    def show(self):

        self.top = tk.Toplevel(self.parent)
        self.top.title('Rigid Registration')

        # Define width and height of this window
        w = 600
        h = 420

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

        self.top.attributes("-topmost", True)

        # StringVars for source and target
        self.source_file = tk.StringVar()
        self.target_file = tk.StringVar()

        # Define style for labelframe
        s = ttk.Style()
        s.configure('Main.TLabelframe.Label', font=('helvetica', 12, 'bold'))

        # Source labelframe
        source_frame = ttk.Labelframe(self.top, text='Source File', style = "Main.TLabelframe")
        source_frame.grid(row=0, padx=15, pady=15, sticky="ew")
        source_frame.columnconfigure(0, weight=1)

        # Message for source
        tk.Message(source_frame, text="Select the moving image to be rigidly registered to the target image", font=("Helvetica", 10), width=500, justify=tk.CENTER).grid(row=0, column=0, padx=1, pady=2, sticky='ew')

        # Source file label
        tk.Label(source_frame,textvariable=self.source_file, font=("Helvetica", 10, 'bold')).grid(row=1, padx=15, pady=15, sticky="ew")

        # Choose source button
        tk.Button(source_frame,text='Choose Source File', command=self.choose_source_file).grid(row=2, padx=5, pady=5)

        # If there is output from the previous step, load the first file as the source file
        try:
            self.source_file.set(self.parent.reorientation_window.reoriented_files[0])
        except:
            # No first file from previous step
            pass

        # Target labelframe
        target_frame = ttk.Labelframe(self.top, text='Target File', style = "Main.TLabelframe")
        target_frame.grid(row=1, padx=15, pady=15, sticky="ew")
        target_frame.columnconfigure(0, weight=1)

        # Message for target
        tk.Message(target_frame, text="Select the fixed target image for the rigid registration", font=("Helvetica", 10), width=500, justify=tk.CENTER).grid(row=0, column=0, padx=1, pady=2, sticky='ew')

        # Target file label
        tk.Label(target_frame,textvariable=self.target_file, font=("Helvetica", 10, 'bold')).grid(row=1, padx=15, pady=15)

        # Choose target button
        tk.Button(target_frame,text='Choose Target File', command=self.choose_target_file).grid(row=2, padx=5, pady=5)

        # If there is output from the previous step, load the second file as the target file
        try:
            self.target_file.set(self.parent.reorientation_window.reoriented_files[1])
        except:
            # No second from previous step
            pass

        # Register button
        tk.Button(self.top,text='Register', command=self.register, width=30, height=2).grid(row=4, padx=5, pady=5)

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

    def register(self):

        # Create the output directory if it doesn't already exist
        output_dir = os.path.join(self.parent.workspace,'step4')
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

        registered, target = rigid(self.source_file.get(),self.target_file.get(), output_dir)

        self.registered_files = []
        self.registered_files.append(registered) # Registered source file
        self.registered_files.append(target) # target fle

        messagebox.showinfo("Done", "Rigid Registration Completed", parent=self.top)

        self.top.destroy()
