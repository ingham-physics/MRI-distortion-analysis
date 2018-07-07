#!/usr/bin/env python3

import os
import subprocess

import logging
logger = logging.getLogger(__name__)

# Runs reorientation
def reorient(input_file, output_path):

    logger.info('Reorienting input file: ' + input_file)
    path, filename = os.path.split(input_file)
    file_base = os.path.join(output_path, filename.split('.')[0])

    # Read origin from input_file
    process = subprocess.Popen(["milxImageInfo", "-o", input_file], stdout=subprocess.PIPE)
    origin, err = process.communicate()
    origin = origin.decode("utf-8").replace('\n','').split('x')

    # Change the orientation to look like a conventional scan:
    file_new_origin = file_base + "_m.nii.gz"
    subprocess.call(["milxImageEditInformation", input_file, file_new_origin, "-m -0 -1 0 1 -0 0 0 0 -1"])
    
    # No-orientate the images: 
    file_no_orient = file_base + "_nO.nii.gz"
    subprocess.call(["milxImageOperations", "-u", file_new_origin, file_no_orient])

    # Re-adjust the origin:
    file_float = file_base + "_float.nii.gz"
    subprocess.call(["milxImageEditInformation", file_no_orient, file_float, "-o", origin[0], origin[1], origin[2]])

    # Multiply the Linac image by 3 to get a better intensity match for generating a mask for the deformation field that incorporates both linac and sim volumes: 
    file_x3 = file_base + "x3.nii.gz"
    subprocess.call(["milxImageOperations", "-C", file_float, "3", file_x3])

    # Convert Image to short data type
    file_linac = file_base + "_Linac.nii.gz"
    subprocess.call(["milxImageConverter", file_float, file_linac, "--componentType", "4"])

    # Convert x3 image to short data type as well
    file_linac_x3 = file_base + "_Linacx3.nii.gz"
    subprocess.call(["milxImageConverter", file_x3, file_linac_x3, "--componentType", "4"])

    # Return the processed file
    return file_linac_x3

    
# Runs when this script is executed directly from the commmand line
if __name__ == "__main__":

    # Original MRI-linac files to be analysed (change file names/location as appropriate): 
    ToOrientateFH="../data/SE_YZ_FH.nii.gz"
    ToOrientateHF="../data/SE_YZ_HF.nii.gz"

    reorient(ToOrientateFH,'.')
    reorient(ToOrientateHF,'.')
