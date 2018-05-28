#!/bin/bash MR-CT_NRR.sh

DStart=`date`
echo $DStart

## For use when looking at comparing the 5 mm CT images to the MRI-linac ones (no interpolation to the 1 mm voxels in this method)

IMG_T="./YZ_HF-FH/CT_cropped.nii.gz"
IMG_S="./YZ_HF-FH/SE_HF_cropped.nii.gz"
OUT_DIR="./YZ_HF-FH/SE_YZ_HF-CT_NRR5"
OUT_PREFX="$OUT_DIR/YZ_HF-CT_NRR"
mkdir -p $OUT_DIR

#BIN="/Dev/nifty_reg-1.3.9/nifty_reg/reg-apps/reg_f3d"
reg_f3d -target "$IMG_T" -source "$IMG_S" -sx 5 -ln 4 -res "${OUT_PREFX}-Result.nii.gz" -cpp "${OUT_PREFX}-CPP.nii.gz"

reg_transform -ref "$IMG_T" -cpp2def "${OUT_PREFX}-CPP.nii.gz" "${OUT_PREFX}-DEF.nii.gz"
reg_transform -ref "$IMG_T" -def2disp "${OUT_PREFX}-DEF.nii.gz" "${OUT_PREFX}-DISP_NIFTY.nii.gz"

# Need to get this part entered into the program properly and not hard coded in like this
BIN="/home/amy/Dev/NiftyRegImageConverter/bin/NiftyRegImageConverter"
$BIN "${OUT_PREFX}-DISP_NIFTY.nii.gz" "${OUT_PREFX}-DISP.nii.gz"

# Export the masked deformation field as a .csv file to then be read (e.g.: by MATLAB) to pull out the deformation numbers 
milxDumpDeformationField "${OUT_PREFX}-DISP.nii.gz" > "${OUT_PREFX}-DeformationField_total.csv"

# Threshold the resulting image to generate a mask to pull out useful regions for distortion quantification
milxImageOperations -t "${OUT_PREFX}-Result.nii.gz" 100 "${OUT_PREFX}_mask.nii.gz"

# Mask the deformation field based on the thresholded image (for visualisation purposes) 
MaskDeformationField "${OUT_PREFX}-DISP.nii.gz" "${OUT_PREFX}_mask.nii.gz" "${OUT_PREFX}-maskedDefField.nii.gz"

# Generate a masked .csv file from the thresholded image
milxDumpDeformationField "${OUT_PREFX}-maskedDefField.nii.gz" "${OUT_PREFX}_mask.nii.gz" >"${OUT_PREFX}-maskedDefField.csv"

DEnd=`date`
echo Started on: $DStart
echo Ended on:   $DEnd
