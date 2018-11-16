#!/usr/bin/env python3
try:
    # Python 2
    import Tkinter as tk
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

from gui.MainWindow import MainWindow
from gui.ConvertDicomWindow import ConvertDicomWindow
from gui.ReorientationWindow import ReorientationWindow
from gui.RigidWindow import RigidWindow
from gui.CropWindow import CropWindow
from gui.DeformationWindow import DeformationWindow
from gui.AnalysisWindow import AnalysisWindow

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

class Workflow():

    def __init__(self, title, msg, steps):

        self.title = title
        self.msg = msg
        self.steps = steps

# Define MRI sim QA workflow
mr_sim_qa_workflow = Workflow('MRI sim QA',
    'Description for MR Sim QA workflow goes here',
    [
        ConvertDicomWindow,
        CropWindow,
        DeformationWindow,
        AnalysisWindow,
    ]
)

# Define MR volunteer/patient workflow
mr_volunteer_patient_workflow = Workflow('MR volunteer/patient',
    'Description for MR volunteer/patient workflow goes here',
    [
        ConvertDicomWindow,
        ReorientationWindow,
        RigidWindow,
        CropWindow,
        DeformationWindow,
        AnalysisWindow,
    ]
)

# Define list of active workflows 
active_workflows = [mr_sim_qa_workflow, mr_volunteer_patient_workflow]

class Application(tk.Frame):

    def __init__(self, parent, *args, **kwargs):

        # Setup this window
        tk.Frame.__init__(self, parent, *args, **kwargs)
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        self.grid(sticky="news")

        self.parent = parent

        tk.Label(self, text="MRI Distortion Analysis", font=("Helvetica", 16)).grid(row=1, padx=10, pady=10)

        s = ttk.Style()
        s.configure('Main.TLabelframe.Label', font=('helvetica', 12, 'bold'))

        # Frame to select workspace
        workspace_frame = ttk.Labelframe(self, text='Workspace', style = "Main.TLabelframe")
        workspace_frame.grid(row=2, column=0, padx=15, pady=15, sticky="ew")
        workspace_frame.columnconfigure(0, weight=1)

        # Message for workspace
        tk.Message(workspace_frame, text="Select the working directory containing the input files", font=("Helvetica", 10), width=500, justify=tk.CENTER).grid(row=0, column=0, padx=1, pady=2, sticky='ew')

        self.str_workspace = tk.StringVar()
        tk.Label(workspace_frame,textvariable=self.str_workspace, font=("Helvetica", 10, 'bold')).grid(row=1, padx=15, pady=15)
        self.workspace = os.path.join(os.getcwd(),'working')
        self.set_workspace(self.workspace)
        tk.Button(workspace_frame,text='Change Workspace', command=self.change_workspace).grid(row=2, padx=5, pady=5)

        # Frame to launch workflow
        workflow_frame = ttk.Labelframe(self, text='Workflow', style = "Main.TLabelframe")
        workflow_frame.grid(row=3, column=0, padx=15, pady=15, sticky="ew")
        workflow_frame.columnconfigure(0, weight=1)

        # Message for workflow frame
        tk.Message(workflow_frame, text="Select the appropriate workflow to begin", font=("Helvetica", 10), width=500, justify=tk.CENTER).grid(row=0, column=0, padx=1, pady=2, sticky='ew')

        # Add buttons for active workflows
        wf_row = 5
        for wf in active_workflows:
            tk.Button(workflow_frame,
                text=wf.title, 
                command= lambda w=wf: self.launch_workflow(w),
                font=("Helvetica", 14, 'bold'),
                width=30, 
                height=4).grid(row=wf_row, padx=10, pady=10)
            wf_row += 1

        self.columnconfigure(0, weight=1)


    def launch_workflow(self, workflow):

        # Prepare Windows
        self.main_window = MainWindow(self)

        prepared_steps = []
        for step in workflow.steps:
            prepared_steps.append(step(self))

        self.parent.withdraw()
        self.main_window.show(workflow.title, workflow.msg, prepared_steps)
        self.parent.deiconify()

    def change_workspace(self):
        file = filedialog.askdirectory(parent=self, initialdir=self.workspace)
        if not type(file)==str or len(file) == 0:
            # Dialog cancelled
            return
        self.workspace = os.path.normpath(file)
        self.set_workspace(self.workspace)

    def set_workspace(self, ws):
        ws = (ws[:10] + '...' + ws[len(ws)-70:]) if len(ws) > 80 else ws
        self.str_workspace.set(ws)

# If running main function, launch MainApplication window
if __name__ == "__main__":

    try:
        root = tk.Tk()
        root.title('MRI Distortion Analysis')

        # Define width and height of this window
        w = 600
        h = 600

        # Place the window in the centre of the screen
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        root.geometry('%dx%d+%d+%d' % (w, h, x, y))

        Application(root).pack(side="top", fill="both", expand=True)

        root.mainloop()
        
    except Exception as e:

        logging.exception("MRI Distortion Analysis Crash")
        messagebox.showerror("Error", "An exception has occured and the application must close: " + type(e).__name__)
