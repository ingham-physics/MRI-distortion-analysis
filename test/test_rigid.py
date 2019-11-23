
import tempfile
import os
import SimpleITK as sitk
import numpy as np

from rigid.rigid import rigid

def test_rigid():

    moving_file = "test/data/rigid/moving.nii.gz"
    target_file = "test/data/rigid/target.nii.gz"
    output_path = tempfile.mkdtemp()

    output_registered, output_target = rigid(moving_file, target_file, output_path)

    im = sitk.ReadImage(output_registered)

    assert im.GetSpacing() == (1.953125, 1.953125, 3.0)
    assert im.GetOrigin() == (0.0, 0.0, 0.0)
    assert im.GetDirection() == (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)

    sif = sitk.StatisticsImageFilter()
    sif.Execute(im)

    assert sif.GetMaximum() == 819.0
    assert sif.GetMinimum() == -51.0
    assert sif.GetMean() == 32.213273299367806
    assert sif.GetVariance() == 1048.6635485315135
    assert sif.GetSum() == 80222905.0

    arr =  sitk.GetArrayFromImage(im)
    assert np.allclose(arr[:,128,128],
                       [0,   0,  -2,  24,  30,  26,  29,  31,  21,  14,
                       47, 187, 287, 178,  58,  35,  27,  23,  25,  26,
                       34,  38,  96, 287, 323, 147,  36,  19,  29,  46,
                       42,  40,  37,  23,  18,  28,  35,  49])
