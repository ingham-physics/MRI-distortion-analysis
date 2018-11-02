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
        self.cropped_files = []

    def show(self):

        self.top = tk.Toplevel(self.parent)
        self.top.title('Crop')
        self.top.geometry('600x1000')
        self.top.update()
        self.top.minsize(self.top.winfo_width(), self.top.winfo_height())
        self.top.resizable(True, True)
        self.top.focus_set()
        self.top.grab_set()

        self.top.attributes("-topmost", True)

        filesFrame = ttk.Labelframe(self.top, text='File Paths')
        filesFrame.grid(row=0, padx=5, pady=5, sticky="news")
        filesFrame.rowconfigure(1, weight=1)

        self.listbox_paths = tk.Listbox(filesFrame)
        self.listbox_paths.grid(row=1, columnspan=1, padx=(5,0), pady=5, sticky='news')
        self.listbox_paths.bind("<<ListboxSelect>>", self.select_file)
        self.selection = self.listbox_paths.curselection()

        vsb = ttk.Scrollbar(filesFrame, orient="vertical", command=self.listbox_paths.yview)
        vsb.grid(row=1, column=2, sticky=("N", "S", "E", "W"), padx=(0,10), pady=(5, 5))
        self.listbox_paths.configure(yscrollcommand=vsb.set)

        filesFrame.columnconfigure(0, weight=1)

        tk.Button(filesFrame,text='Add File', command=self.add_file, width=20).grid(row=0, padx=5, pady=5)
        tk.Button(filesFrame,text='Remove Selected', command=self.remove_file, width=20).grid(row=2, padx=5, pady=5)

        plot_frame = ttk.Labelframe(self.top, text='Crop Image')
        plot_frame.grid(row=1, padx=15, pady=15, sticky="ew")
        self.strVarXfrom = tk.StringVar()
        self.strVarXto = tk.StringVar()
        self.strVarYfrom = tk.StringVar()
        self.strVarYto = tk.StringVar()
        self.strVarZfrom = tk.StringVar()
        self.strVarZto = tk.StringVar()
        param_frame = ttk.Labelframe(self.top, text='Cropping Parameters')
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

        # Add the files from the previous steps
        try:
            for f in self.parent.rigid_window.registered_files:
                self.insert_file(f)
        except:
            # User hasn't run previous step
            pass

    def select_file(self, a):
        if len(self.listbox_paths.curselection()) > 3:
            for i in self.listbox_paths.curselection():
                if i not in self.selection:
                    self.listbox_paths.selection_clear(i)
        self.selection = self.listbox_paths.curselection()

        self.load_image(self.listbox_paths.get(self.listbox_paths.curselection()))

    def update_units(self):
        if self.units.get() == 1: # mm
            self.strVarXfrom.set("{:.2f}".format(self.physFrom[0]))
            self.strVarXto.set("{:.2f}".format(self.physTo[0]))
            self.strVarYfrom.set("{:.2f}".format(self.physFrom[1]))
            self.strVarYto.set("{:.2f}".format(self.physTo[1]))
            self.strVarZfrom.set("{:.2f}".format(self.physFrom[2]))
            self.strVarZto.set("{:.2f}".format(self.physTo[2]))
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
        
        # Clamp the values to be in range of image
        sz = self.img.GetSize()
        indFrom = self.img.TransformPhysicalPointToIndex(self.physFrom)
        indTo = self.img.TransformPhysicalPointToIndex(self.physTo)

        indFrom = (max(indFrom[0],0), max(indFrom[1],0), max(indFrom[2],0))
        indFrom = (min(indFrom[0],sz[0]), min(indFrom[1],sz[1]), min(indFrom[2],sz[2]))
        indTo = (max(indTo[0],0), max(indTo[1],0), max(indTo[2],0))
        indTo = (min(indTo[0],sz[0]), min(indTo[1],sz[1]), min(indTo[2],sz[2]))
        
        self.physFrom = self.img.TransformIndexToPhysicalPoint(indFrom)
        self.physTo = self.img.TransformIndexToPhysicalPoint(indTo)
        
        self.update_units()

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

    def load_image(self, img_file):

        try:
            self.img=sitk.ReadImage(img_file)
        except:
            print('File read failed ' + img_file )
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

        if not hasattr(self, 'physFrom'):
            self.physFrom = self.img.TransformIndexToPhysicalPoint((0,0,0))
            self.physTo = self.img.TransformIndexToPhysicalPoint(self.img.GetSize())

        self.update_units()

        self.entry_changed()

    def insert_file(self, f):
        self.listbox_paths.insert(tk.END, f)
        self.listbox_paths.select_clear(0,tk.END)
        self.listbox_paths.select_set(tk.END)

        self.selection = self.listbox_paths.curselection()

        self.load_image(self.listbox_paths.get(self.listbox_paths.curselection()))

    def add_file(self):

        initial_dir = self.parent.workspace
        
        if self.listbox_paths.size() > 0:
            initial_dir = os.path.dirname(self.listbox_paths.get(tk.END))
            
        f = filedialog.askopenfilename(parent=self.top, initialdir=initial_dir)
        if len(f) == 0:
            # Cancelled
            return
        f = os.path.normpath(f)

        self.insert_file(f)
       
    def remove_file(self):

        selected_indexes = self.listbox_paths.curselection()

        for ind in selected_indexes:
            self.listbox_paths.delete(int(ind))

        self.listbox_paths.select_set(tk.END)

    def crop(self):

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

        # Crop each image loaded to physical coords
        self.cropped_files = []
        for i, img_file in enumerate(self.listbox_paths.get(0, tk.END)):
            logger.info('Cropping: ' + img_file)

            # Determine output file name
            path, filename = os.path.split(img_file)
            file_base = os.path.join(output_dir, filename.split('.')[0])
            output_file = file_base + '_cropped.nii.gz'


            # Convert the physical coordinates to the voxels coords for this image
            img = sitk.ReadImage(img_file)
            indFrom = img.TransformPhysicalPointToIndex(self.physFrom)
            indTo = img.TransformPhysicalPointToIndex(self.physTo)

            # Crop the image
            crop = sitk.CropImageFilter()
            lowerBoundary = [indFrom[0],
                indFrom[1],
                indFrom[2]]
            crop.SetLowerBoundaryCropSize(indFrom)

            size = self.img.GetSize()
            upperBoundary = [size[0]-indTo[0],
                size[1]-indTo[1],
                size[2]-indTo[2]]
            crop.SetUpperBoundaryCropSize(upperBoundary)

            cropped_image = crop.Execute ( img )

            # Save the file
            writer = sitk.ImageFileWriter()
            writer.SetFileName ( output_file )
            writer.Execute ( cropped_image )

            self.cropped_files.append(output_file)


        messagebox.showinfo("Done", "Image(s) Cropped", parent=self.top)

        self.top.destroy()
