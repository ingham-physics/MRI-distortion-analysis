
import tempfile
import os
import SimpleITK as sitk
import numpy as np

from MRL_deformable.mrl_deformable import mrl_deformable

def test_deform():

    moving_file = "test/data/deform/moving.nii.gz"
    target_file = "test/data/deform/target.nii.gz"
    output_path = tempfile.mkdtemp()

    output_csv, output_masked_df = mrl_deformable(moving_file, target_file, output_path)

    # Compare output files with known ground truth
    df_gt_file = "test/data/deform/GT.nii.gz"
    csv_gt_file = "test/data/deform/GT.csv"

    df = sitk.ReadImage(output_masked_df)
    df_gt = sitk.ReadImage(df_gt_file)

    assert df.GetSpacing() == df_gt.GetSpacing()
    assert df.GetOrigin() == df_gt.GetOrigin()
    assert df.GetDirection() == df_gt.GetDirection()

    arr =  sitk.GetArrayFromImage(df)
    arr_gt = sitk.GetArrayFromImage(df_gt)
    assert np.allclose(arr, arr_gt)

    csv = np.genfromtxt(output_csv, delimiter=',', skip_header=2)
    csv_gt = np.genfromtxt(csv_gt_file, delimiter=',', skip_header=2)
    assert np.allclose(csv, csv_gt)
