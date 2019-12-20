#!/usr/bin/env python3

import os
import SimpleITK as sitk

import logging
logger = logging.getLogger(__name__)

# Converts Dicom to Nifti
def convert_dicom(input_dir, output_file):

    logger.info('Converting Dicom in directory: ' + input_dir)

    success = True

    try:
        reader = sitk.ImageSeriesReader()

        dicom_names = reader.GetGDCMSeriesFileNames( input_dir )
        reader.SetFileNames(dicom_names)

        image = reader.Execute()

        sitk.WriteImage( image, output_file )

        logger.info("Files converted from " + input_dir + " written to " + output_file)
    except Exception as e:
        logger.exception(e)
        success = False

    return success

# Runs when this script is executed directly from the commmand line
if __name__ == "__main__":

    dicom_dir="./dicom"
    output_file="converted.nii.gz"

    convert_dicom(dicom_dir, output_file)
