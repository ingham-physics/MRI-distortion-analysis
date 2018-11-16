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
        self.title = 'Analysis'
        #self.deformed_files = []

    def show(self):

        self.top = tk.Toplevel(self.parent)
        self.top.title('Analysis')

        # Define width and height of this window
        w = 600
        h = 700

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

        # StringVars
        self.csv_file = tk.StringVar()
        self.def_file = tk.StringVar()

        # Define style for labelframe
        s = ttk.Style()
        s.configure('Main.TLabelframe.Label', font=('helvetica', 12, 'bold'))

        # CSV Label frame
        csv_frame = ttk.Labelframe(self.top, text='Registration CSV File', style = "Main.TLabelframe")
        csv_frame.grid(row=0, padx=15, pady=15, sticky="ew")
        csv_frame.columnconfigure(0, weight=1)

        # Message for csv
        tk.Message(csv_frame, text="Description goes here", font=("Helvetica", 10), width=500, justify=tk.CENTER).grid(row=0, column=0, padx=1, pady=2, sticky='ew')

        tk.Label(csv_frame,textvariable=self.csv_file, font=("Helvetica", 10, 'bold')).grid(row=1, padx=15, pady=15)
        tk.Button(csv_frame,text='Choose Registration CSV File', command=self.choose_csv_file).grid(row=2, padx=5, pady=5)

        def_frame = ttk.Labelframe(self.top, text='Masked Deformation Field File', style = "Main.TLabelframe")
        def_frame.grid(row=1, padx=15, pady=15, sticky="ew")
        def_frame.columnconfigure(0, weight=1)

        # Message for def
        tk.Message(def_frame, text="Description goes here", font=("Helvetica", 10), width=500, justify=tk.CENTER).grid(row=0, column=0, padx=1, pady=2, sticky='ew')

        tk.Label(def_frame,textvariable=self.def_file, font=("Helvetica", 10, 'bold')).grid(row=1, padx=15, pady=15)
        tk.Button(def_frame,text='Choose Masked Deformation Field', command=self.choose_def_file).grid(row=2, padx=5, pady=5)

        iso_frame = ttk.Labelframe(self.top, text='ISO Centre', style = "Main.TLabelframe")
        iso_frame.grid(row=2, padx=15, pady=15, ipadx=15, ipady=15, sticky="ew")
        iso_frame.columnconfigure(2, weight=1)

        # Message for iso
        tk.Message(iso_frame, text="Description goes here", font=("Helvetica", 10), width=500, justify=tk.CENTER).grid(row=0, columnspan=3, padx=1, pady=2, sticky='ew')

        tk.Label(iso_frame, text='x:', justify=tk.RIGHT).grid(row=1, column=0, padx=10, pady=10)
        tk.Label(iso_frame, text='y:', justify=tk.RIGHT).grid(row=2, column=0, padx=10, pady=10)
        tk.Label(iso_frame, text='z:', justify=tk.RIGHT).grid(row=3, column=0, padx=10, pady=10)
        self.iso_x = tk.Entry(iso_frame, width=10)
        self.iso_x.insert(tk.END, '0')
        self.iso_y = tk.Entry(iso_frame, width=10)
        self.iso_y.insert(tk.END, '0')
        self.iso_z = tk.Entry(iso_frame, width=10)
        self.iso_z.insert(tk.END, '0')

        self.iso_x.grid(row=1, column=1)
        self.iso_y.grid(row=2, column=1)
        self.iso_z.grid(row=3, column=1)

        tk.Button(self.top,text='Analyse', command=self.analyse, width=30, height=2).grid(row=4, padx=5, pady=5)

        # Add the files from the previous steps
        try:
            self.csv_file.set(self.parent.deformation_window.deformed_files[0])
            self.def_file.set(self.parent.deformation_window.deformed_files[1])
        except:
            # User hasn't run previous step
            pass

        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(5, weight=1)

        # This is a modal window so wait until it is closed
        self.top.wait_window()

    def choose_csv_file(self):
        initial_dir = os.path.dirname(self.csv_file.get())
        if len(initial_dir) == 0:
            initial_dir = self.parent.workspace
        file = filedialog.askopenfilename(parent=self.top, initialdir=initial_dir)
        if not type(file)==str or len(file) == 0:
            # Dialog cancelled
            return
        self.csv_file.set(os.path.normpath(file))

    def choose_def_file(self):
        initial_dir = os.path.dirname(self.def_file.get())
        if len(initial_dir) == 0:
            initial_dir = self.parent.workspace
        file = filedialog.askopenfilename(parent=self.top, initialdir=initial_dir)
        if not type(file)==str or len(file) == 0:
            # Dialog cancelled
            return
        self.def_file.set(os.path.normpath(file))

    def analyse(self):

        # Validate input CSV
        if not os.path.isfile(self.csv_file.get()):
            messagebox.showerror("Error", "Registration CSV file not found", parent=self.top)
            return

        # Validate input Deformation file
        if not os.path.isfile(self.def_file.get()):
            messagebox.showerror("Error", "Deformation file not found", parent=self.top)
            return

        # Validate ISO Centre
        try:
            iso = [float(self.iso_x.get()), float(self.iso_y.get()), float(self.iso_z.get())]
        except ValueError:
            messagebox.showerror("Error", "Ensure ISO Center is entered correctly", parent=self.top)
            return

        # Create the output directory if it doesn't already exist
        output_dir = os.path.join(self.parent.workspace,'step8')
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

        perform_analysis(self.csv_file.get(), output_dir, iso, def_file=self.def_file.get())

        messagebox.showinfo("Done", "Analysis Completed", parent=self.top)
