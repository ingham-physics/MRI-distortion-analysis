#!/usr/bin/env python3
import matplotlib
matplotlib.use('TkAgg')

from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from pylab import *
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

import SimpleITK as sitk
from crop.util import ImageAxes

import logging
logger = logging.getLogger(__name__)

class CropWindow:

    def __init__(self, parent):

        self.parent = parent

    def show(self):

        self.top = tk.Toplevel(self.parent)
        self.top.title('Crop')
        self.top.geometry('600x800')
        self.top.update()
        self.top.minsize(self.top.winfo_width(), self.top.winfo_height())
        self.top.resizable(True, True)
        self.top.focus_set()
        self.top.grab_set()

        self.top.attributes("-topmost", True)

        self.source_file = tk.StringVar()
        source_frame = ttk.Labelframe(self.top, text='Image file to crop')
        source_frame.grid(row=0, padx=15, pady=15, sticky="ew")
        tk.Label(source_frame,textvariable=self.source_file, font=("Helvetica", 10)).grid(row=1, padx=15, pady=15)
        tk.Button(source_frame,text='Choose Image File', command=self.choose_source_file).grid(row=2, padx=5, pady=5)

        plot_frame = ttk.Labelframe(self.top, text='Crop Image')
        plot_frame.grid(row=1, padx=15, pady=15, sticky="ew")
        #tk.Label(source_frame,textvariable=self.source_file, font=("Helvetica", 10)).grid(row=1, padx=15, pady=15)
        #tk.Button(source_frame,text='Choose Registration CSV File', command=self.choose_source_file).grid(row=2, padx=5, pady=5)

        self.xFrom = tk.StringVar()
        self.xTo = tk.StringVar()
        self.yFrom = tk.StringVar()
        self.yTo = tk.StringVar()
        self.zFrom = tk.StringVar()
        self.zTo = tk.StringVar()
        param_frame = ttk.Labelframe(self.top, text='Cropping Parameters')
        param_frame.grid(row=3, padx=15, pady=15, sticky="ew")
        tk.Label(param_frame,text='X', font=("Helvetica", 10)).grid(row=1, column=2, padx=0, pady=0)
        tk.Label(param_frame,text='Y', font=("Helvetica", 10)).grid(row=1, column=3, padx=0, pady=0)
        tk.Label(param_frame,text='Z', font=("Helvetica", 10)).grid(row=1, column=4, padx=0, pady=0)
        tk.Label(param_frame,text='From:', font=("Helvetica", 10)).grid(row=2, column=1, padx=0, pady=0)
        tk.Label(param_frame,text='To:', font=("Helvetica", 10)).grid(row=3, column=1, padx=0, pady=0)
        tk.Entry(param_frame, textvariable=self.xFrom, width=10).grid(row=2, column=2, padx=15, pady=15)
        tk.Entry(param_frame, textvariable=self.xTo, width=10).grid(row=3, column=2, padx=15, pady=15)
        tk.Entry(param_frame, textvariable=self.yFrom, width=10).grid(row=2, column=3, padx=15, pady=15)
        tk.Entry(param_frame, textvariable=self.yTo, width=10).grid(row=3, column=3, padx=15, pady=15)
        tk.Entry(param_frame, textvariable=self.zFrom, width=10).grid(row=2, column=4, padx=15, pady=15)
        tk.Entry(param_frame, textvariable=self.zTo, width=10).grid(row=3, column=4, padx=15, pady=15)

        tk.Button(self.top,text='Crop', command=self.crop, width=30, height=2).grid(row=4, padx=5, pady=5)

        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(1, weight=1)

        fig = Figure(figsize=(5, 5), dpi=100)
        self.axAx = fig.add_subplot(2,2,1)
        self.axCor = fig.add_subplot(2,2,2)
        self.axSag = fig.add_subplot(2,2,3)

        self.canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def rect_selected(self, rect, axis):

        if axis == 0: # Axial
            self.xFrom.set(int(rect[0][0]))
            self.xTo.set(int(rect[1][0]))
            self.yFrom.set(int(rect[0][1]))
            self.yTo.set(int(rect[1][1]))
        if axis == 1: # Coronal
            self.xFrom.set(int(rect[0][0]))
            self.xTo.set(int(rect[1][0]))
            self.zFrom.set(int(rect[0][1]))
            self.zTo.set(int(rect[1][1]))
        if axis == 2: # Sagittal
            self.yFrom.set(int(rect[0][0]))
            self.yTo.set(int(rect[1][0]))
            self.zFrom.set(int(rect[0][1]))
            self.zTo.set(int(rect[1][1]))
            
    def load_image(self):

        try:
            img=sitk.ReadImage(self.source_file.get())
        except:
            print('File read failed ' + self.source_file.get() )
            raise

        self.xFrom.set('0')
        self.xTo.set(str(img.GetWidth()))

        self.yFrom.set('0')
        self.yTo.set(str(img.GetHeight()))

        self.zFrom.set('0')
        self.zTo.set(str(img.GetDepth()))
        
        self.imAx = ImageAxes(0, self.axAx, img, self.rect_selected)
        self.imCor = ImageAxes(1, self.axCor, img, self.rect_selected)
        self.imSag = ImageAxes(2, self.axSag, img, self.rect_selected)
        self.canvas.draw()


    def choose_source_file(self):
        file = filedialog.askopenfilename(parent=self.top, initialdir=self.source_file.get())
        if not type(file)==str or len(file) == 0:
            # Dialog cancelled
            return
        self.source_file.set(os.path.normpath(file))

        self.load_image()

    def crop(self):

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
