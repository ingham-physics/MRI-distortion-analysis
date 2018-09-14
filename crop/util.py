from matplotlib.widgets import  RectangleSelector
from matplotlib.widgets import TextBox
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle

import SimpleITK as sitk

# Takes care of rendering the appropriate image slice on to the axis
class ImageAxes(object):
        
    def onselect(self, eclick, erelease):
        self.rect_selected([(eclick.xdata, eclick.ydata), (erelease.xdata, erelease.ydata)], self.axis)

    def __init__(self, axis, axes, data, rect_selected):

        self.data = data
        self.nda_data = sitk.GetArrayFromImage(data)
        self.overlays = []
        self.rect_selected = rect_selected

        self.axis = axis
        self.axes = axes
        self.slice = int(self.nda_data.shape[self.axis]/2)
        self.xSlices = slice(None)
        self.ySlices = slice(None)
        self.zSlices = slice(None)

        self.xFrom = 0
        self.yFrom = 0
        self.zFrom = 0
        size = self.data.GetSize()

        rectprops = dict(facecolor='red', edgecolor = 'black', alpha=0.5, fill=True)
        self.rectangleSelector = RectangleSelector(axes, self.onselect, drawtype='box', rectprops=rectprops)
        self.dimName = 'Axial'
        if self.axis == 0: # Axial
            self.xSlices = self.slice
            self.aspect = data.GetSpacing()[0]/data.GetSpacing()[1]
            self.origin = 'upper'
            self.dimName = 'Axial'
            self.xTo = size[0]
            self.yTo = size[1]
            self.zTo = size[2]
        if self.axis == 1: # Coronal
            self.ySlices = self.slice
            self.aspect = data.GetSpacing()[2]/data.GetSpacing()[0]
            self.origin = 'lower'
            self.dimName = 'Coronal'
            self.xTo = size[0]
            self.yTo = size[2]
            self.zTo = size[1]
        if self.axis == 2: # Sagittal
            self.zSlices = self.slice
            self.aspect = data.GetSpacing()[2]/data.GetSpacing()[1]
            self.origin = 'lower'
            self.dimName = 'Sagittal'
            self.xTo = size[1]
            self.yTo = size[2]
            self.zTo = size[0]

        self.image = axes.imshow(self.nda_data[self.xSlices,self.ySlices,self.zSlices], cmap='gray', aspect=self.aspect, origin=self.origin)
        axes.axis('off')

        self.rect = Rectangle((self.xFrom, self.yFrom), self.xTo-self.xFrom, self.yTo-self.yFrom, 
            facecolor='g', alpha=0.3, edgecolor='None')
        self.axes.add_artist(self.rect)

        self.update()

    def onscroll(self, event):
        if event.inaxes == self.axes:

            self.slice = self.slice + event.step

            if self.slice < 0:
                self.slice = 0
            
            if self.slice >= self.nda_data.shape[self.axis]:
                self.slice = self.nda_data.shape[self.axis]-1

            self.update()

    def set_selected_region(self, xf, yf, zf, xt, yt, zt):
        self.xFrom = xf
        self.yFrom = yf
        self.zFrom = zf
        self.xTo = xt
        self.yTo = yt
        self.zTo = zt

        self.update()

    def update(self):
        if self.axis == 0:
            self.xSlices = self.slice
            #slice_mm = self.data.TransformIndexToPhysicalPoint((0,0,self.slice))[2]
        if self.axis == 1:
            self.ySlices = self.slice
            #slice_mm = self.data.TransformIndexToPhysicalPoint((0,self.slice,0))[1]
        if self.axis == 2:
            self.zSlices = self.slice
            #slice_mm = self.data.TransformIndexToPhysicalPoint((self.slice,0,0))[0]

        self.axes.set_title(self.dimName + " (Slice: "+str(self.slice)+")")

        self.image.set_data(self.nda_data[self.xSlices,self.ySlices,self.zSlices])

        # Update the rect overlay
        self.rect.set_x(self.xFrom)
        self.rect.set_y(self.yFrom)
        self.rect.set_width(self.xTo-self.xFrom)
        self.rect.set_height(self.yTo-self.yFrom)

        # Hide rect if not on this slice
        if self.slice < self.zFrom or self.slice > self.zTo:
            self.rect.set_width(0)
            self.rect.set_height(0)

        self.image.axes.figure.canvas.draw()