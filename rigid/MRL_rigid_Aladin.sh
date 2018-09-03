#!/bin/bash MRL_rigid_Aladin_PAROT.sh

DStart=`date`
echo $DStart

IMG_T="./step1/PAROT_PV_Sim0.nii.gz" # This is the target image 
IMG_S="./step2/PAROT_PV_Linac0_KZ_Linac.nii.gz" # The second image is the moving image
OUT_DIR="./Rigid"
# This output should resemble the direction of rigid registration. 1st part=moving; 2nd part=fixed target. Moving-fixed_rig
OUT_PREFX="$OUT_DIR/Linac0-Sim_rig"
mkdir -p $OUT_DIR

# Move MRI-sim & MRL origins to 0,0,0
# label: "Move MRI-sim & MRL origins to assist in achieving a rigid registration"
milxImageEditInformation "$IMG_T" "Sim_origin.nii.gz" -o "-200" "-180.417" "107.5"

#Rigid registration with Aladin: 
#BIN="/Dev/nifty_reg-1.3.9/nifty_reg/reg-apps/reg_aladin"
reg_aladin -ref "Sim_origin.nii.gz" -flo "$IMG_S" -res "${OUT_PREFX}-Aladin.nii.gz" -rigOnly -aff "${OUT_PREFX}-Aladin.txt"

#RegRig + ' -ref ' + refImg + ' -flo ' + movImg + ' -res ' + rigResult + ' -rigOnly -aff ' + rigTfm  


DEnd=`date`
echo Started on: $DStart
echo Ended on:   $DEnd

echo Please check rigid result


## Other rigid reg options 
#BIN="/home/amy/Dev/milx-view/build/bin/milxAliBaba"
#mirorr -t rigid -f "$IMG_T" -m "$IMG_S" -a 0 -c 3 -n 0 --save-moving "${OUT_PREFX}-Result.nii.gz" -l "${OUT_PREFX}-Result.tfm" --fresh --do-not-register 

#BIN="/home/amy/Dev/milx-view/build/bin/milxAliBaba"
#mirorr -t rigid -f "$IMG_T" -m "${OUT_PREFX}-Result.nii.gz" -a 0 -c 3 -n 0 --save-moving "${OUT_PREFX2}-Result.nii.gz" -l "${OUT_PREFX2}-Result.tfm" --fresh 
