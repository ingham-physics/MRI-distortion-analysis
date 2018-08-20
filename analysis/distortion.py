#!/usr/bin/env python3

import os
import subprocess

import numpy as np

import logging
logger = logging.getLogger(__name__)

# Runs distortion analysis
def perform_analysis(def_field_file, iso=[0,0,0]):

    logger.info('Analysing file: ' + def_field_file)
    #path, filename = os.path.split(def_field_file)
    #file_base = os.path.join(output_path, filename.split('.')[0])

    # Read data from csv into d
    d = np.genfromtxt(def_field_file, delimiter=',',skip_header=2)

    # Offset the positions to the iso centre
    d[:,0:3] = d[:,0:3]-iso

    # Compute each vector's magnitude
    mags = np.sqrt(np.power(d[:,3:4],2)+np.power(d[:,4:5],2)+np.power(d[:,5:6],2))

    mag_max = np.max(mags)
    mag_min = np.min(mags)
    mag_mean = np.mean(mags)
    mag_std = np.std(mags)
    logger.info('Max magnitude: ' + str(mag_max))
    logger.info('Mn magnitude: ' + str(mag_min))
    logger.info('Mean magnitude: ' + str(mag_mean))
    logger.info('Std magnitude: ' + str(mag_std))

    logger.info('Analysis complete')

    #return file_masked_csv

# Runs when this script is executed directly from the commmand line
if __name__ == "__main__":

    def_field="./CT-maskedDefField.csv"

    analysis(def_field, [119, 100, 35])
