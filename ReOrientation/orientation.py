#!/usr/bin/env python3

import os
import subprocess

import SimpleITK as sitk

import logging
logger = logging.getLogger(__name__)

# Runs reorientation
def reorient(input_file, output_path):

    logger.info('Reorienting input file: ' + input_file)
    path, filename = os.path.split(input_file)
    file_base = os.path.join(output_path, filename.split('.')[0])

    # Read origin from input_file
    img = sitk.ReadImage(input_file)
    origin = img.GetOrigin()

    # Change the orientation to look like a conventional scan:
    file_new_origin = file_base + "_m.nii.gz"
    img = sitk.ReadImage(input_file)
    img.SetDirection((0, 1, 0, 1, 0, 0, 0, 0, -1))
    sitk.WriteImage(img, file_new_origin)

    # No-orientate the images:
    file_no_orient = file_base + "_nO.nii.gz"
    subprocess.call(["milxImageOperations", "-u", file_new_origin, file_no_orient])

    # Re-adjust the origin:
    file_float = file_base + "_float.nii.gz"
    img = sitk.ReadImage(file_no_orient)
    img.SetOrigin(origin)
    sitk.WriteImage(img, file_float)

    # Multiply the Linac image by 3 to get a better intensity match for generating a
    # mask for the deformation field that incorporates both linac and sim volumes:
    file_x3 = file_base + "x3.nii.gz"
    img = sitk.ReadImage(file_float)
    img = img * 3
    sitk.WriteImage(img, file_x3)

    # Convert Image to short data type
    file_linac = file_base + "_Linac.nii.gz"
    img = sitk.ReadImage(file_float)
    img = sitk.Cast(img, sitk.sitkInt16)
    sitk.WriteImage(img, file_linac)

    # Convert x3 image to short data type as well
    file_linac_x3 = file_base + "_Linacx3.nii.gz"
    img = sitk.ReadImage(file_x3)
    img = sitk.Cast(img, sitk.sitkInt16)
    sitk.WriteImage(img, file_linac_x3)

    logger.info('Reorientation complete')

    # Return the reoriented file
    return file_linac


# Runs when this script is executed directly from the commmand line
if __name__ == "__main__":

    # Original MRI-linac files to be analysed (change file names/location as appropriate): 
    ToOrientateFH="../data/SE_YZ_FH.nii.gz"
    ToOrientateHF="../data/SE_YZ_HF.nii.gz"

    reorient(ToOrientateFH,'.')
    reorient(ToOrientateHF,'.')
