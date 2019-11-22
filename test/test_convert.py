
import tempfile
import os
import SimpleITK as sitk

from convert.convert import convert_dicom

def test_convert():
    print(os.getcwd())

    dicom_dir = "test/data/dicom"
    output_file = tempfile.mktemp() + ".nii.gz"

    success = convert_dicom(dicom_dir, output_file)
    assert success

    im = sitk.ReadImage(output_file)

    assert im.GetSpacing() == (1.953125, 1.953125, 3.0)
    assert im.GetOrigin() == (7.5, -250.0, 250.0)
    assert im.GetDirection() == (-0.0, 0.0, -1.0, 1.0, -0.0, 0.0, 0.0, -1.0, 0.0)

    sif = sitk.StatisticsImageFilter()
    sif.Execute(im)

    assert sif.GetMaximum() == 1027.0
    assert sif.GetMinimum() == 0.0
    assert sif.GetMean() == 36.626527886641654
    assert sif.GetVariance() == 1578.7199914455948
    assert sif.GetSum() == 91213533.0
