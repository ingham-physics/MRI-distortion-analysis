#!/usr/bin/env python3

import os
import subprocess

import SimpleITK as sitk
import numpy as np

import logging
logger = logging.getLogger(__name__)

def convert_nifty_reg_image(nifty_file, output_file):

    # Read the nifty file
    reader = sitk.ImageFileReader()
    reader.SetFileName(nifty_file)
    reader.ReadImageInformation()

    # Extract only the dims we want
    extract_size = list(reader.GetSize()[:3]) + [0, 3]
    reader.SetExtractSize(extract_size)

    # Shift the image dims to what SimpleITK expects
    img = reader.Execute()
    arr = sitk.GetArrayFromImage(img)
    out = sitk.GetImageFromArray(np.moveaxis(arr, 0, -1))

    # Update the image information with the correct dims
    extract_size = list(reader.GetSize()[:3]) + [0, 0]
    reader.SetExtractSize(extract_size)
    img = reader.Execute()
    out.CopyInformation(img)

    # Write the output file
    sitk.WriteImage(out, output_file)


def dump_deformation_field(deformation_field, output_file, mask_file=None, connected_components=False):

    # Read the deformation field
    img = sitk.ReadImage(deformation_field)

    # Read the mask if one was supplied
    mask = None
    if mask_file:
        mask = sitk.ReadImage(mask_file)

    # Write the output to a file
    f = open(output_file, "w")
    f.write("Input Filename = {0}\n".format(deformation_field))

    if mask_file:
        f.write("Mask Filename = {0}\n".format(mask_file))

    if connected_components:

        cc = sitk.ConnectedComponent(mask)

        lssif = sitk.LabelShapeStatisticsImageFilter()
        lssif.Execute(cc)

        for c in lssif.GetLabels():
            centroid = lssif.GetCentroid(c)
            pix_centroid = cc.TransformPhysicalPointToIndex(centroid)
            value = img.GetPixel(pix_centroid)
            f.write("{0}, {1}, {2}, {3}, {4}, {5}\n".format(pix_centroid[0], pix_centroid[1], pix_centroid[2], value[0], value[1], value[2]))
    else:
        for z in range(img.GetSize()[2]):
            for y in range(img.GetSize()[1]):
                for x in range(img.GetSize()[0]):

                    if mask:
                        if not mask.GetPixel((x,y,z)):
                            continue

                    value = img.GetPixel((x,y,z))
                    f.write("{0}, {1}, {2}, {3}, {4}, {5}\n".format(x, y, z, value[0], value[1], value[2]))

    f.close()


def mask_deformation_field(deformation_field, mask_file, output_file):

    df = sitk.ReadImage(deformation_field)
    mask = sitk.ReadImage(mask_file)
    mask_arr = sitk.GetArrayFromImage(mask)
    mask_arr = np.repeat(mask_arr[:, :, :, np.newaxis], 3, axis=3)

    df_arr = sitk.GetArrayFromImage(df)
    df_arr = df_arr * mask_arr

    out = sitk.GetImageFromArray(df_arr)
    out.CopyInformation(df)

    sitk.WriteImage(out, output_file)


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
    convert_nifty_reg_image(file_disp_nifty, file_disp)

    # Export the masked deformation field as a .csv file to then be read (e.g.: by MATLAB) to pull out the deformation numbers 
    file_total = file_base + "DeformationField_total.csv"
    dump_deformation_field(file_disp, file_total)

    # Threshold the resulting image to generate a mask to pull out useful regions for distortion quantification
    file_mask = file_base + "_mask.nii.gz"
    img = sitk.ReadImage(file_result)
    out = sitk.BinaryThreshold(img, lowerThreshold=threshold, upperThreshold=1000000, insideValue=1, outsideValue=0)
    sitk.WriteImage(out, file_mask)

    # Mask the deformation field based on the thresholded image (for visualisation purposes)
    file_masked_df = file_base + "-maskedDefField.nii.gz"
    mask_deformation_field(file_disp, file_mask, file_masked_df)

    # Generate a masked .csv file from the thresholded image
    file_masked_csv = file_base + "-maskedDefField.csv"
    dump_deformation_field(file_masked_df, file_masked_csv, mask_file=file_mask)

    # Dump the values to .csv by dumping only the centroid of each connected component
    dump_deformation_field(file_masked_df, file_masked_csv, mask_file=file_mask, connected_components=True)

    logger.info('Deformation complete')

    # Return masked csv and the masked deformation field
    return file_masked_csv, file_masked_df

# Runs when this script is executed directly from the commmand line
if __name__ == "__main__":

    # Original files to be analysed (change file names/location as appropriate):
    IMG_T="./YZ_HF-FH/CT_cropped.nii.gz"
    IMG_S="./YZ_HF-FH/SE_HF_cropped.nii.gz"
    OUT_DIR="./YZ_HF-FH/SE_YZ_HF-CT_NRR5"

    mrl_deformable(IMG_S, IMG_T, OUT_DIR)
