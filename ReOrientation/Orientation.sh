#!/bin/bash Orientation.sh

DStart=`date`
echo $DStart

# Original MRI-linac files to be analysed (change file names/location as appropriate): 
ToOrientateFH="./YZ_HF-FH/SE_YZ_FH.nii.gz" 
ToOrientateHF="./YZ_HF-FH/SE_YZ_HF.nii.gz" 

# Definition of files for use further on: 
NewOriginFH="./YZ_HF-FH/SE_YZ_FH_m.nii.gz"
NoOrientFH="./YZ_HF-FH/SE_YZ_FH_nO.nii.gz"
FloatFH="./YZ_HF-FH/SE_YZ_FH_float.nii.gz"

NewOriginHF="./YZ_HF-FH/SE_YZ_HF_m.nii.gz"
NoOrientHF="./YZ_HF-FH/SE_YZ_HF_nO.nii.gz"
FloatHF="./YZ_HF-FH/SE_YZ_HF_float.nii.gz"

# Add in the origin coordinate from original MRL image (change/input if appropriate): 
x="103.5"
y="-250"
z="250"

# Change the orientation to look like a conventional scan: 
milxImageEditInformation "$ToOrientateFH" "$NewOriginFH" -m -0 -1 0 1 -0 0 0 0 -1
milxImageEditInformation "$ToOrientateHF" "$NewOriginHF" -m -0 -1 0 1 -0 0 0 0 -1

# No-orientate the images: 
milxImageOperations -u "$NewOriginFH" "$NoOrientFH"
milxImageOperations -u "$NewOriginHF" "$NoOrientHF"

# Re-adjust the origin: 
milxImageEditInformation "$NoOrientFH" "$FloatFH" -o "$x" "$y" "$z"
milxImageEditInformation "$NoOrientHF" "$FloatHF" -o "$x" "$y" "$z"

# Multiply the Linac image by 3 to get a better intensity match for generating a mask for the deformation field that incorporates both linac and sim volumes: 
milxImageOperations -C "$FloatFH" 3 "./YZ_HF-FH/SE_YZ_FHx3.nii.gz"
milxImageOperations -C "$FloatHF" 3 "./YZ_HF-FH/SE_YZ_HFx3.nii.gz"

# Convert Image to short data type
milxImageConverter "$FloatFH" "./YZ_HF-FH/Linac_YZ_FH.nii.gz" --componentType 4
milxImageConverter "$FloatHF" "./YZ_HF-FH/Linac_YZ_HF.nii.gz" --componentType 4

milxImageConverter "./YZ_HF-FH/SE_YZ_FHx3.nii.gz" "./YZ_HF-FH/Linac_YZ_FHx3.nii.gz" --componentType 4
milxImageConverter "./YZ_HF-FH/SE_YZ_HFx3.nii.gz" "./YZ_HF-FH/Linac_YZ_HFx3.nii.gz" --componentType 4

DEnd=`date`
echo Started on: $DStart
echo Ended on:   $DEnd

