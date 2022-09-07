# Geometric Distortion Assessment

This document provides instructions for the MRI distortion QA tool. 

Further details of this work can be found at: 
Walker A, Chlap P, Causer T, Mahmood F, Buckley J,Holloway L. Development of a vendor neutral MRI distortion quality assurance workflow. J Appl Clin Med Phys. 2022;(00):e13735. https://doi.org/10.1002/acm2.13735

## Background
The geometric uncertainties in MRI due to magnetic field inhomogeneities and grandient non-linearities are well known. When utilising MRI for radiotherapy treatment planning, it is important that these distortions are known so that their impact can be minimised in the treatment planning process. This tool provides a vendor neutral solution to performing MRI distortion quality assurance (QA) by way of deformable registrtaion of an object (phantom) of known geometry as visualised on CT. 

## Image requirements: 
- CT image of test object 
    - Visualisation of test object on CT should match that of MRI. And attenuation visible on CT but not on MR should be thresholded and masked out of the CT image to ensure appropriate registrtaion between the 2 datasets 
- MR image of test object 
    - Test object should be designed and scanned to minimise susceptibility and chemical shift artefacts 
    - ** **Make note of the scanner isocentre location with respect to the phantom geometry as this is required for the analysis step** **

 > Further details on these requirements can be found at: 
 >
 > Walker A., et al., "Continuous table acquisition MRI for radiotherapy treatment planning: Distortion assessment with a new extended 3D volumetric phantom," Medical Physics. Vol. 42(4), 2015, pp. 1982-1991. https://aapm.onlinelibrary.wiley.com/doi/abs/10.1118/1.4915920 


![Example setup of a geometric test phantom on MR!](https://user-images.githubusercontent.com/111952735/186548980-d9415a01-ad61-406e-8a96-4a44ee517ac9.jpg)



## Online tool 
The 



## Test data


Add links here to a test dataset with the known output results 