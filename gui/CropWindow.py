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
        self.strVarXfrom = tk.StringVar()
        #self.strVarXfrom.trace("w", lambda name, index, mode, sv=self.strVarXfrom: self.update_selection())
        self.strVarXto = tk.StringVar()
        #self.strVarXto.trace("w", lambda name, index, mode, sv=self.strVarXto: self.update_selection())
        self.strVarYfrom = tk.StringVar()
        #self.strVarYfrom.trace("w", lambda name, index, mode, sv=self.strVarYfrom: self.update_selection())
        self.strVarYto = tk.StringVar()
        #self.strVarYto.trace("w", lambda name, index, mode, sv=self.strVarYto: self.update_selection())
        self.strVarZfrom = tk.StringVar()
        #self.strVarZfrom.trace("w", lambda name, index, mode, sv=self.strVarZfrom: self.update_selection())
        self.strVarZto = tk.StringVar()
        #self.strVarZto.trace("w", lambda name, index, mode, sv=self.strVarZto: self.update_selection())
        param_frame = ttk.Labelframe(self.top, text='Cropping Parameters (Voxels)')
        param_frame.grid(row=3, padx=15, pady=15, sticky="ew")
        tk.Label(param_frame,text='X', font=("Helvetica", 10)).grid(row=1, column=2, padx=0, pady=0)
        tk.Label(param_frame,text='Y', font=("Helvetica", 10)).grid(row=1, column=3, padx=0, pady=0)
        tk.Label(param_frame,text='Z', font=("Helvetica", 10)).grid(row=1, column=4, padx=0, pady=0)
        tk.Label(param_frame,text='From:', font=("Helvetica", 10)).grid(row=2, column=1, padx=0, pady=0)
        tk.Label(param_frame,text='To:', font=("Helvetica", 10)).grid(row=3, column=1, padx=0, pady=0)
        entXFrom = tk.Entry(param_frame, textvariable=self.strVarXfrom, width=10)
        entXFrom.grid(row=2, column=2, padx=15, pady=15)
        entXFrom.bind ("<Return>",  (lambda _: self.entry_changed()))
        entXFrom.bind ("<FocusOut>",  (lambda _: self.entry_changed()))
        entXto = tk.Entry(param_frame, textvariable=self.strVarXto, width=10)
        entXto.grid(row=3, column=2, padx=15, pady=15)
        entXto.bind ("<Return>",  (lambda _: self.entry_changed()))
        entXto.bind ("<FocusOut>",  (lambda _: self.entry_changed()))
        entYFrom = tk.Entry(param_frame, textvariable=self.strVarYfrom, width=10)
        entYFrom.grid(row=2, column=3, padx=15, pady=15)
        entYFrom.bind ("<Return>",  (lambda _: self.entry_changed()))
        entYFrom.bind ("<FocusOut>",  (lambda _: self.entry_changed()))
        entYTo = tk.Entry(param_frame, textvariable=self.strVarYto, width=10)
        entYTo.grid(row=3, column=3, padx=15, pady=15)
        entYTo.bind ("<Return>",  (lambda _: self.entry_changed()))
        entYTo.bind ("<FocusOut>",  (lambda _: self.entry_changed()))
        entZFrom = tk.Entry(param_frame, textvariable=self.strVarZfrom, width=10)
        entZFrom.grid(row=2, column=4, padx=15, pady=15)
        entZFrom.bind ("<Return>",  (lambda _: self.entry_changed()))
        entZFrom.bind ("<FocusOut>",  (lambda _: self.entry_changed()))
        entZTo = tk.Entry(param_frame, textvariable=self.strVarZto, width=10)
        entZTo.grid(row=3, column=4, padx=15, pady=15)
        entZTo.bind ("<Return>",  (lambda _: self.entry_changed()))
        entZTo.bind ("<FocusOut>",  (lambda _: self.entry_changed()))

        # Radio buttons for Units (voxels or mm)
        self.units = tk.IntVar()
        tk.Radiobutton(param_frame, text="mm", variable=self.units, value=1,
                command = lambda : self.update_units()).grid(row=2, column=5, padx=15, pady=15)
        tk.Radiobutton(param_frame, text="voxels", variable=self.units, value=2,
                command = lambda : self.update_units()).grid(row=3, column=5, padx=15, pady=15)
        self.units.set(1)

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

    def update_units(self):
        if self.units.get() == 1: # mm
            self.strVarXfrom.set(str(self.physFrom[0]))
            self.strVarXto.set(str(self.physTo[0]))
            self.strVarYfrom.set(str(self.physFrom[1]))
            self.strVarYto.set(str(self.physTo[1]))
            self.strVarZfrom.set(str(self.physFrom[2]))
            self.strVarZto.set(str(self.physTo[2]))
        else: # voxels
            indFrom = self.img.TransformPhysicalPointToIndex(self.physFrom)
            indTo = self.img.TransformPhysicalPointToIndex(self.physTo)
            self.strVarXfrom.set(str(indFrom[0]))
            self.strVarXto.set(str(indTo[0]))
            self.strVarYfrom.set(str(indFrom[1]))
            self.strVarYto.set(str(indTo[1]))
            self.strVarZfrom.set(str(indFrom[2]))
            self.strVarZto.set(str(indTo[2]))

    def entry_changed(self):
        # Read values from entry fields and update the phys coords
        if self.units.get() == 1: # mm
            self.physFrom = (float(self.strVarXfrom.get()), float(self.strVarYfrom.get()), float(self.strVarZfrom.get()) )
            self.physTo = (float(self.strVarXto.get()), float(self.strVarYto.get()), float(self.strVarZto.get()) )
        else: # voxels
            indFrom = (int(self.strVarXfrom.get()), int(self.strVarYfrom.get()), int(self.strVarZfrom.get()) )
            indTo = (int(self.strVarXto.get()), int(self.strVarYto.get()), int(self.strVarZto.get()) )

            self.physFrom = self.img.TransformIndexToPhysicalPoint(indFrom)
            self.physTo = self.img.TransformIndexToPhysicalPoint(indTo)

        self.update_selection()

    def rect_selected(self, rect, axis):

        indFrom = self.img.TransformPhysicalPointToIndex(self.physFrom)
        indTo = self.img.TransformPhysicalPointToIndex(self.physTo)

        if axis == 0: # Axial
            indFrom = (int(rect[0][0]), int(rect[0][1]), indFrom[2]) 
            indTo = (int(rect[1][0]), int(rect[1][1]), indTo[2])
        if axis == 1: # Coronal
            indFrom = (int(rect[0][0]), indFrom[1], int(rect[0][1])) 
            indTo = (int(rect[1][0]), indTo[1], int(rect[1][1]))
        if axis == 2: # Sagittal
            indFrom = (indFrom[0], int(rect[0][0]), int(rect[0][1])) 
            indTo = (indTo[0], int(rect[1][0]), int(rect[1][1]))

        self.physFrom = self.img.TransformIndexToPhysicalPoint(indFrom)
        self.physTo = self.img.TransformIndexToPhysicalPoint(indTo)
        self.update_units()

        self.update_selection()

    def update_selection(self):

        # Determine the voxel coords to updates the axes
        try:
            indFrom = self.img.TransformPhysicalPointToIndex(self.physFrom)
            indTo = self.img.TransformPhysicalPointToIndex(self.physTo)

            self.imAx.set_selected_region(
                indFrom[0],
                indFrom[1],
                indFrom[2],
                indTo[0],
                indTo[1], 
                indTo[2])

            self.imCor.set_selected_region(
                indFrom[0],
                indFrom[2],
                indFrom[1],
                indTo[0],
                indTo[2],
                indTo[1])

            self.imSag.set_selected_region(
                indFrom[1],
                indFrom[2],
                indFrom[0],
                indTo[1],
                indTo[2],
                indTo[0])
        except AttributeError as e:
            # Occurs when no image has been loaded yet
            # We can safely ignore
            print(e)
            pass
        except ValueError as e:
            print(e)
            # Occurs when an invalid character is entered
            pass



    def load_image(self):

        try:
            self.img=sitk.ReadImage(self.source_file.get())
        except:
            print('File read failed ' + self.source_file.get() )
            messagebox.showerror("Error", "An error occurred while reading the input file", parent=self.top)
            return

        self.axAx.clear()
        self.axCor.clear()
        self.axSag.clear()
        
        self.imAx = ImageAxes(0, self.axAx, self.img, self.rect_selected)
        self.imCor = ImageAxes(1, self.axCor, self.img, self.rect_selected)
        self.imSag = ImageAxes(2, self.axSag, self.img, self.rect_selected)
        self.canvas.draw()
        self.canvas.mpl_connect('scroll_event', self.imAx.onscroll)
        self.canvas.mpl_connect('scroll_event', self.imCor.onscroll)
        self.canvas.mpl_connect('scroll_event', self.imSag.onscroll)

        self.physFrom = self.img.TransformIndexToPhysicalPoint((0,0,0))
        print(self.img.GetSize())
        self.physTo = self.img.TransformIndexToPhysicalPoint(self.img.GetSize())

        self.update_units()

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

        lowerBoundary = [int(self.strVarXfrom.get()),
            int(self.strVarYfrom.get()),
            int(self.strVarZfrom.get())]
        crop.SetLowerBoundaryCropSize(lowerBoundary)

        size = self.img.GetSize()
        upperBoundary = [size[0]-int(self.strVarXto.get()),
            size[1]-int(self.strVarYto.get()),
            size[2]-int(self.strVarZto.get())]
        crop.SetUpperBoundaryCropSize(upperBoundary)

        cropped_image = crop.Execute ( self.img )

        # Save the file
        writer = sitk.ImageFileWriter()
        writer.SetFileName ( output_file )
        writer.Execute ( cropped_image )

        messagebox.showinfo("Done", "Image Cropped", parent=self.top)

        self.top.destroy()
