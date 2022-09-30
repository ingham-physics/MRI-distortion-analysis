import tempfile
import os
import SimpleITK as sitk
import numpy as np
import pytest

from ReOrientation.orientation import reorient


@pytest.mark.skip()
def test_reorient():

    nifti_file = "test/data/reorient/nifti.nii.gz"
    output_path = tempfile.mkdtemp()

    output_file = reorient(nifti_file, output_path)

    im = sitk.ReadImage(output_file)

    assert im.GetSpacing() == (1.953125, 1.953125, 3.0)
    assert im.GetOrigin() == (7.5, -250.0, 250.0)
    assert im.GetDirection() == (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)

    sif = sitk.StatisticsImageFilter()
    sif.Execute(im)

    assert sif.GetMaximum() == 1027.0
    assert sif.GetMinimum() == 0.0
    assert sif.GetMean() == 36.626527886641654
    assert sif.GetVariance() == 1578.7199914455948
    assert sif.GetSum() == 91213533.0

    arr = sitk.GetArrayFromImage(im)
    assert np.allclose(
        arr[:, 128, 128],
        [
            40,
            324,
            257,
            27,
            32,
            26,
            25,
            38,
            16,
            15,
            17,
            185,
            356,
            219,
            46,
            40,
            20,
            24,
            25,
            19,
            28,
            47,
            38,
            293,
            394,
            125,
            26,
            14,
            23,
            60,
            43,
            41,
            39,
            16,
            12,
            38,
            25,
            51,
        ],
    )
