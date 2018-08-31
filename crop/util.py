from matplotlib.widgets import  RectangleSelector
from matplotlib.widgets import TextBox
import matplotlib.patches as patches

import SimpleITK as sitk

class CropDim():

    def submitText(self, text):

        try:
            self.crop_from = int(self.fromTextBox.text)
            self.crop_to = int(self.toTextBox.text)
        except Exception as e:
            print(e)
            self.fromTextBox.set_val(str(self.crop_from))
            self.toTextBox.set_val(str(self.crop_to))

    def __init__(self, size, pos, dim):

        self.size = size
        self.crop_from = 0
        self.crop_to = size

        self.fromTextBox = TextBox(plt.axes([0.6, pos, 0.1, 0.05]), dim + ' From:', initial="0")
        self.fromTextBox.on_submit(self.submitText)

        self.toTextBox = TextBox(plt.axes([0.8, pos, 0.1, 0.05]), 'To:', initial=str(size))
        self.toTextBox.on_submit(self.submitText)

    def setFrom(self, val):
        self.crop_from = int(val)
        self.fromTextBox.set_val(str(self.crop_from))
        update_patches()

    def setTo(self, val):
        self.crop_to = int(val)
        self.toTextBox.set_val(str(self.crop_to))
        update_patches()

class CropParams():

    def __init__(self, data):

        self.x = CropDim(data.GetWidth(), 0.8, 'X')
        self.y = CropDim(data.GetHeight(), 0.7, 'Y')
        self.z = CropDim(data.GetDepth(), 0.6, 'Z')

class ImageAxes(object):
        
    def onselect(self, eclick, erelease):
        self.rect_selected([(eclick.xdata, eclick.ydata), (erelease.xdata, erelease.ydata)], self.axis)

    def __init__(self, axis, axes, data, rect_selected):

        self.data = data
        self.nda_data = sitk.GetArrayFromImage(data)
        self.overlays = []
        self.overlay_images = []
        self.rect_selected = rect_selected

        self.axis = axis
        self.axes = axes
        self.slice = int(self.nda_data.shape[self.axis]/2)
        self.xSlices = slice(None)
        self.ySlices = slice(None)
        self.zSlices = slice(None)

        rectprops = dict(facecolor='red', edgecolor = 'black',
                 alpha=0.5, fill=True)
        self.rectangleSelector = RectangleSelector(axes, self.onselect, drawtype='box', rectprops=rectprops)
        print(data.GetSpacing())
        self.dimName = 'Axial'
        if self.axis == 0: # Axial
            self.xSlices = self.slice
            self.aspect = data.GetSpacing()[0]/data.GetSpacing()[1]
            self.origin = 'upper'
            self.dimName = 'Axial'
        if self.axis == 1: # Coronal
            self.ySlices = self.slice
            self.aspect = data.GetSpacing()[2]/data.GetSpacing()[0]
            self.origin = 'lower'
            self.dimName = 'Coronal'
        if self.axis == 2: # Sagittal
            self.zSlices = self.slice
            self.aspect = data.GetSpacing()[2]/data.GetSpacing()[1]
            self.origin = 'lower'
            self.dimName = 'Sagittal'
        print(self.aspect)

        self.image = axes.imshow(self.nda_data[self.xSlices,self.ySlices,self.zSlices], cmap='gray', aspect=self.aspect, origin=self.origin)
        axes.axis('off')

        #self.text = self.axes.text(0.01, 0.93, '', fontsize=11, color=(1.0,1.0,1.0,), transform=self.axes.transAxes)

        self.update_depth(self.slice)

    def update_depth(self, val):
        self.slice = int(round(val))
        if self.axis == 0:
            self.xSlices = self.slice
            slice_mm = self.data.TransformIndexToPhysicalPoint((0,0,self.slice))[2]
        if self.axis == 1:
            self.ySlices = self.slice
            slice_mm = self.data.TransformIndexToPhysicalPoint((0,self.slice,0))[1]
        if self.axis == 2:
            self.zSlices = self.slice
            slice_mm = self.data.TransformIndexToPhysicalPoint((self.slice,0,0))[0]

        #self.text.set_text(self.dimName+' Slice: '+str(self.slice)+' ('+str(round(slice_mm,1))+'mm)')
        self.image.set_data(self.nda_data[self.xSlices,self.ySlices,self.zSlices])

        for i in range(len(self.overlay_images)):
            self.overlay_images[i].set_data(self.overlays[i][self.xSlices,self.ySlices,self.zSlices])
