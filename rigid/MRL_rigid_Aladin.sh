#!/bin/bash MRL_rigid_Aladin.sh

DStart=`date`
echo $DStart

IMG_T="./Orig_scriptTest/Linac_AP_FFc.nii.gz" # Using the MRL image seems to work better here. Therefore everything in MRL (reoriented) space
IMG_S="Sim_tse_LR_BW814.nii.gz" # The second image is the moving image
OUT_DIR="./Orig_scriptTest/Rigid/"
OUT_PREFX="$OUT_DIR/Sim-Linac_ignore"
OUT_PREFX2="$OUT_DIR/Sim-Linac_rig"
mkdir -p $OUT_DIR

#Rigid reg with Aladin: 
BIN="/Dev/nifty_reg-1.3.9/nifty_reg/reg-apps/reg_aladin"
reg_aladin -ref "$IMG_T" -flo "$IMG_S" -res "${OUT_PREFX2}-Aladin.nii.gz" -rigOnly #-"${OUT_PREFX2}-Aladin.tfm"

#RegRig + ' -ref ' + refImg + ' -flo ' + movImg + ' -res ' + rigResult + ' -rigOnly -aff ' + rigTfm  

#BIN="/home/amy/Dev/milx-view/build/bin/milxAliBaba"
#mirorr -t rigid -f "$IMG_T" -m "$IMG_S" -a 0 -c 3 -n 0 --save-moving "${OUT_PREFX}-Result.nii.gz" -l "${OUT_PREFX}-Result.tfm" --fresh --do-not-register 

#BIN="/home/amy/Dev/milx-view/build/bin/milxAliBaba"
#mirorr -t rigid -f "$IMG_T" -m "${OUT_PREFX}-Result.nii.gz" -a 0 -c 3 -n 0 --save-moving "${OUT_PREFX2}-Result.nii.gz" -l "${OUT_PREFX2}-Result.tfm" --fresh 

DEnd=`date`
echo Started on: $DStart
echo Ended on:   $DEnd

echo Please check rigid result

