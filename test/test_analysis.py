import tempfile
import os
import SimpleITK as sitk
import numpy as np

from analysis.distortion import perform_analysis


def test_deform():

    def_field = "test/data/deform/GT.csv"
    gt_file = "test/data/deform/"

    output_path = tempfile.mkdtemp()

    output_file = perform_analysis(
        def_field, output_path, [119, 100, 35], px_spacing=[1.195312, 1.195312, 3]
    )

    expected_lines = [
        "Max magnitude: 0.00010235907122832006\n",
        "Min magnitude: 0.0\n",
        "Mean magnitude: 2.2443263236124706e-05\n",
        "Std magnitude: 1.804639462735981e-05\n",
    ]

    with open(output_file, "r") as f:
        for expected in expected_lines:
            assert f.readline() == expected
