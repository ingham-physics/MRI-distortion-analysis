#!/usr/bin/env python3
import matplotlib
matplotlib.use('TkAgg')

from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec

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
        self.xFrom = tk.StringVar()
        self.xFrom.trace("w", lambda name, index, mode, sv=self.xFrom: self.update_selection())
        self.xTo = tk.StringVar()
        self.xTo.trace("w", lambda name, index, mode, sv=self.xTo: self.update_selection())
        self.yFrom = tk.StringVar()
        self.yFrom.trace("w", lambda name, index, mode, sv=self.yFrom: self.update_selection())
        self.yTo = tk.StringVar()
        self.yTo.trace("w", lambda name, index, mode, sv=self.yTo: self.update_selection())
        self.zFrom = tk.StringVar()
        self.zFrom.trace("w", lambda name, index, mode, sv=self.zFrom: self.update_selection())
        self.zTo = tk.StringVar()
        self.zTo.trace("w", lambda name, index, mode, sv=self.zTo: self.update_selection())
        param_frame = ttk.Labelframe(self.top, text='Cropping Parameters (Voxels)')
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

        fig = Figure(figsize=(50, 50), dpi=75)
        rect = fig.patch
        rect.set_facecolor("lightgray")
        gs = GridSpec(2, 2)
        gs.update(wspace=0.000025, hspace=0.0005)

        self.axAx = fig.add_subplot(gs[0], frameon=False)
        self.axAx.get_xaxis().set_visible(False)
        self.axAx.get_yaxis().set_visible(False)

        self.axCor = fig.add_subplot(gs[1], frameon=False)
        self.axCor.get_xaxis().set_visible(False)
        self.axCor.get_yaxis().set_visible(False)

        self.axSag = fig.add_subplot(gs[2], frameon=False)
        self.axSag.get_xaxis().set_visible(False)
        self.axSag.get_yaxis().set_visible(False)

        fig.subplots_adjust(bottom=0.05, top=0.95, left=0, right=1)   

        self.canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Add the file from the previous step
        try:
            f = self.parent.reorientation_window.reoriented_files[0]
            self.source_file.set(os.path.normpath(f))
            self.load_image()
        except:
            # User hasn't run previous step
            pass

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

        self.update_selection()

    def update_selection(self):
    
        try:
            self.imAx.set_selected_region(
                int(self.xFrom.get()),
                int(self.yFrom.get()),
                int(self.zFrom.get()),
                int(self.xTo.get()), 
                int(self.yTo.get()), 
                int(self.zTo.get()))

            self.imCor.set_selected_region(
                int(self.xFrom.get()),
                int(self.zFrom.get()),
                int(self.yFrom.get()),
                int(self.xTo.get()), 
                int(self.zTo.get()), 
                int(self.yTo.get()))

            self.imSag.set_selected_region(
                int(self.yFrom.get()), 
                int(self.zFrom.get()), 
                int(self.xFrom.get()), 
                int(self.yTo.get()), 
                int(self.zTo.get()), 
                int(self.xTo.get()))
        except AttributeError:
            # Occurs when no image has been loaded yet
            # We can safely ignore
            pass
        except ValueError:
            # Occurs when an invalid character is entered
            pass



    def load_image(self):

        try:
            self.img=sitk.ReadImage(self.source_file.get())
        except:
            print('File read failed ' + self.source_file.get() )
            messagebox.showerror("Error", "An error occurred while reading the input file", parent=self.top)
            return
        
        self.imAx = ImageAxes(0, self.axAx, self.img, self.rect_selected)
        self.imCor = ImageAxes(1, self.axCor, self.img, self.rect_selected)
        self.imSag = ImageAxes(2, self.axSag, self.img, self.rect_selected)
        self.canvas.draw()
        self.canvas.mpl_connect('scroll_event', self.imAx.onscroll)
        self.canvas.mpl_connect('scroll_event', self.imCor.onscroll)
        self.canvas.mpl_connect('scroll_event', self.imSag.onscroll)

        self.xFrom.set('0')
        self.xTo.set(str(self.img.GetWidth()))

        self.yFrom.set('0')
        self.yTo.set(str(self.img.GetHeight()))

        self.zFrom.set('0')
        self.zTo.set(str(self.img.GetDepth()))

    def choose_source_file(self):
        file = filedialog.askopenfilename(parent=self.top, initialdir=self.source_file.get())
        if not type(file)==str or len(file) == 0:
            # Dialog cancelled
            return
        self.source_file.set(os.path.normpath(file))

        self.load_image()

    def crop(self):

        # Set output file name
        if len(self.source_file.get()) == 0:
            messagebox.showwarning("No Image", "No image loaded", parent=self.top)
            return

        # Create the output directory if it doesn't already exist
        output_dir = os.path.join(self.parent.workspace,'step5')
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

        # Determine output file name
        path, filename = os.path.split(self.source_file.get())
        file_base = os.path.join(output_dir, filename.split('.')[0])
        output_file = file_base + '_cropped.nii.gz'

        # Crop the image
        crop = sitk.CropImageFilter()

        lowerBoundary = [int(self.xFrom.get()),
            int(self.yFrom.get()),
            int(self.zFrom.get())]
        crop.SetLowerBoundaryCropSize(lowerBoundary)

        size = self.img.GetSize()
        upperBoundary = [size[0]-int(self.xTo.get()),
            size[1]-int(self.yTo.get()),
            size[2]-int(self.zTo.get())]
        crop.SetUpperBoundaryCropSize(upperBoundary)

        cropped_image = crop.Execute ( self.img )

        # Save the file
        writer = sitk.ImageFileWriter()
        writer.SetFileName ( output_file )
        writer.Execute ( cropped_image )

        messagebox.showinfo("Done", "Image Cropped", parent=self.top)

        self.top.destroy()
