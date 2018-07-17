#!/usr/bin/env python3

import os
import subprocess

import logging
logger = logging.getLogger(__name__)

# Runs reorientation
def mrl_deformable(source_file, target_file, output_path, grid_spacing=25, threshold=100):

    logger.info('Deforming source : ' + source_file + ' to target: ' + target_file)
    path, filename = os.path.split(source_file)
    file_base = os.path.join(output_path, filename.split('.')[0])

    file_result = file_base + "-Result.nii.gz"
    file_cpp = file_base + "-CPP.nii.gz"
    subprocess.call(["reg_f3d", "-target", target_file, "-source", source_file, "-sx", str(grid_spacing), "-ln", "4", "-res", file_result, "-cpp", file_cpp])

    file_def = file_base + "-DEF.nii.gz"
    subprocess.call(["reg_transform", "-ref", target_file, "-cpp2def", file_cpp, file_def])
    file_disp_nifty = file_base + "-DISP_NIFTY.nii.gz"
    subprocess.call(["reg_transform", "-ref", target_file, "-def2disp", file_def, file_disp_nifty])

    file_disp = file_base + "-DISP.nii.gz"
    subprocess.call(["NiftyRegImageConverter", file_disp_nifty, file_disp])

    # Export the masked deformation field as a .csv file to then be read (e.g.: by MATLAB) to pull out the deformation numbers 
    file_total = file_base + "DeformationField_total.csv"
    f = open(file_total, "w")
    subprocess.call(["milxDumpDeformationField", file_disp], stdout=f)

    # Threshold the resulting image to generate a mask to pull out useful regions for distortion quantification
    file_mask = file_base + "_mask.nii.gz"
    subprocess.call(["milxImageOperations", "-t", file_result, str(threshold), file_mask])

    # Mask the deformation field based on the thresholded image (for visualisation purposes) 
    file_masked_df = file_base + "-maskedDefField.nii.gz"
    subprocess.call(["MaskDeformationField", file_disp, file_mask, file_masked_df])

    # Generate a masked .csv file from the thresholded image
    file_masked_csv = file_base + "-maskedDefField.csv"
    f = open(file_masked_csv, "w")
    subprocess.call(["milxDumpDeformationField", file_masked_df, file_mask], stdout=f)

    logger.info('Deformation complete')

    # Return masked csv
    return file_masked_csv

# Runs when this script is executed directly from the commmand line
if __name__ == "__main__":

    # Original files to be analysed (change file names/location as appropriate): 
    IMG_T="./YZ_HF-FH/CT_cropped.nii.gz"
    IMG_S="./YZ_HF-FH/SE_HF_cropped.nii.gz"
    OUT_DIR="./YZ_HF-FH/SE_YZ_HF-CT_NRR5"
    
    mrl_deformable(IMG_S, IMG_T, OUT_DIR)
