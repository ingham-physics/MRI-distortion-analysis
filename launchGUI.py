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

import datetime, logging, sys, os, decimal, subprocess

from gui.ConvertDicomWindow import ConvertDicomWindow
from gui.ReorientationWindow import ReorientationWindow

# Log to file and stdout
log_file_name = 'logs/'+datetime.datetime.today().strftime('%Y')+'/'+datetime.datetime.today().strftime('%m')+'/MRIDA_'+datetime.datetime.today().strftime('%Y-%m-%d_%H_%M_%S')+'.log'
try:
    # Python 3
    os.makedirs(os.path.dirname(log_file_name), exist_ok=True) # > Python 3.2
except TypeError:
    # Python 2
    try:
        os.makedirs(os.path.dirname(log_file_name))
    except OSError:
        if not os.path.isdir(os.path.dirname(log_file_name)):
            raise

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=log_file_name,
                    filemode='w')

# define a new Handler to log to console as well
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logger = logging.getLogger('')
logger.addHandler(console)

logger.info('MRI Distortion Analysis')

class Application(tk.Frame):

    def __init__(self, parent, *args, **kwargs):

        # Setup this window
        tk.Frame.__init__(self, parent, *args, **kwargs)
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        self.grid(sticky="news")

        self.parent = parent

        tk.Label(self, text="MRI Distortion Analysis", font=("Helvetica", 16)).grid(row=1, padx=10, pady=10)

        workspaceFrame = ttk.Labelframe(self, text='Workspace')
        workspaceFrame.grid(row=2, padx=15, pady=15)

        self.str_workspace = tk.StringVar()
        tk.Label(workspaceFrame,textvariable=self.str_workspace, font=("Helvetica", 10)).grid(row=1, padx=15, pady=15)
        self.workspace = os.path.join(os.getcwd(),'working')
        self.set_workspace(self.workspace)
        tk.Button(workspaceFrame,text='Change Workspace', command=self.change_workspace).grid(row=2, padx=5, pady=5)


        tk.Button(self,text='Step 1: Convert DICOM Files', command=self.convert_dicom, width=30, height=2).grid(row=5, padx=10, pady=10)
        tk.Button(self,text='Step 2: Reorientation', command=self.reorientation, width=30, height=2).grid(row=6, padx=10, pady=10)
        tk.Button(self,text='Step 3: Masking', command=self.reorientation, width=30, height=2, state=tk.DISABLED).grid(row=7, padx=10, pady=10)
        tk.Button(self,text='Step 4: Rigid Registration', command=self.reorientation, width=30, height=2, state=tk.DISABLED).grid(row=8, padx=10, pady=10)
        tk.Button(self,text='Step 5: Crop', command=self.reorientation, width=30, height=2, state=tk.DISABLED).grid(row=9, padx=10, pady=10)
        tk.Button(self,text='Step 6: Deformable Registration', command=self.reorientation, width=30, height=2, state=tk.DISABLED).grid(row=10, padx=10, pady=10)
        tk.Button(self,text='Step 7: Masking', command=self.reorientation, width=30, height=2, state=tk.DISABLED).grid(row=11, padx=10, pady=10)
        tk.Button(self,text='Step 8: Analysis', command=self.reorientation, width=30, height=2, state=tk.DISABLED).grid(row=12, padx=10, pady=10)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Prepare Windows
        self.convert_dicom_window = ConvertDicomWindow(self)
        self.reorientation_window = ReorientationWindow(self)

    def convert_dicom(self):
        self.convert_dicom_window.show()

    def reorientation(self):
        self.reorientation_window.show()

    def change_workspace(self):
        file = filedialog.askdirectory(parent=self, initialdir=self.workspace)
        if not type(file)==str or len(file) == 0:
            # Dialog cancelled
            return
        self.workspace = os.path.normpath(file)
        self.set_workspace(self.workspace)

    def set_workspace(self, ws):
        ws = (ws[:10] + '...' + ws[len(ws)-30:]) if len(ws) > 40 else ws
        self.str_workspace.set(ws)

# If running main function, launch MainApplication window
if __name__ == "__main__":

    try:
        root = tk.Tk()
        root.title('MRI Distortion Analysis')
        root.geometry('400x680')

        Application(root).pack(side="top", fill="both", expand=True)

        root.mainloop()
        
    except Exception as e:

        logging.exception("MRI Distortion Analysis Crash")
        messagebox.showerror("Error", "An exception has occured and the application must close: " + type(e).__name__)
