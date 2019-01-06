#!/usr/bin/env python3

import os
import subprocess

import logging
logger = logging.getLogger(__name__)

# Runs reorientation
def rigid(source_file, target_file, output_path):

    logger.info('Rigid registration from source : ' + source_file + ' to target: ' + target_file)
    path, filename_source = os.path.split(source_file)
    file_base_source = os.path.join(output_path, filename_source.split('.')[0])
    path, filename_target = os.path.split(target_file)
    file_base_target = os.path.join(output_path, filename_target.split('.')[0])

    # Move to origin 0,0,0
    file_source_origin = file_base_source + "-ORIGIN.nii.gz"
    subprocess.call(["milxImageEditInformation", source_file, file_source_origin, "-o", "0", "0", "0"])
    file_target_origin = file_base_target + "-ORIGIN.nii.gz"
    subprocess.call(["milxImageEditInformation", target_file, file_target_origin, "-o", "0", "0", "0"])

    #Rigid registration with Aladin: 
    file_rigid_reg = file_base_source + "-Aladin.nii.gz"
    file_rigid_reg_txt = file_base_source + "-Aladin.txt"
    subprocess.call(["reg_aladin", "-ref", file_target_origin, "-flo", file_source_origin, "-res", file_rigid_reg, "-nac", "-maxit", 10, "-rigOnly", "-aff", file_rigid_reg_txt])
    
    # Return registered file and target file
    return file_rigid_reg, file_target_origin

# Runs when this script is executed directly from the commmand line
if __name__ == "__main__":

    # Original files to be registered (change file names/location as appropriate): 
    IMG_T="./step1/PAROT_PV_Sim0.nii.gz" # This is the target image 
    IMG_S="./step2/PAROT_PV_Linac0_KZ_Linac.nii.gz" # The second image is the moving image
    OUT_DIR="./Rigid"
    
    rigid(IMG_S, IMG_T, OUT_DIR)
