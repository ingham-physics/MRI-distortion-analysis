#!/usr/bin/env python3
try:
    # Python 2
    import Tkinter  as tk
    import tkMessageBox as messagebox
except ImportError:
    # Python 3
    import tkinter as tk
    from tkinter import messagebox

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

        tk.Label(self, text="MRI Distortion Analysis", font=("Helvetica", 16)).grid(row=1, padx=5, pady=5)

        tk.Button(self,text='Step 1: Convert DICOM Files', command=self.convert_dicom, width=30, height=2).grid(row=2, padx=5, pady=5)
        tk.Button(self,text='Step 2: Reorientation', command=self.reorientation, width=30, height=2).grid(row=3, padx=5, pady=5)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(6, weight=1)

        # Prepare Windows
        self.convert_dicom_window = ConvertDicomWindow(self)
        self.reorientation_window = ReorientationWindow(self)

    def add_file(self):

        self.directory = os.path.normpath(filedialog.askdirectory(parent=self))
        self.listbox_paths.insert(tk.END, self.directory)

    def convert_dicom(self):
        self.convert_dicom_window.show()

    def reorientation(self):
        self.reorientation_window.show()

# If running main function, launch MainApplication window
if __name__ == "__main__":

    try:
        root = tk.Tk()
        root.title('MRI Distortion Analysis')
        root.geometry('400x600')

        Application(root).pack(side="top", fill="both", expand=True)

        root.mainloop()
        
    except Exception as e:

        logging.exception("MRI Distortion Analysis Crash")
        messagebox.showerror("Error", "An exception has occured and the application must close: " + type(e).__name__)
