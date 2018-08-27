#!/usr/bin/env python3

import os
import subprocess

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

import logging
logger = logging.getLogger(__name__)

# Runs distortion analysis
def perform_analysis(def_csv_file, output_dir, iso=[0,0,0], px_spacing=[1,1,1], def_file=None):

    logger.info('Analysing file: ' + def_csv_file)
    path, filename = os.path.split(def_csv_file)
    file_base = os.path.join(output_dir, filename.split('.')[0])
    logger.info('Using ISO: ' + str(iso))

    if(def_file):
        # Read origin from def_file
        process = subprocess.Popen(["milxImageInfo", "-s", def_file], stdout=subprocess.PIPE)
        pxs, err = process.communicate()
        px_spacing = pxs.decode("utf-8").replace('\n','').split('x')
        px_spacing = [float(p) for p in px_spacing] # Convert to float
        
    logger.info('Using Pixel Spacing: ' + str(px_spacing))

    # Read data from csv into d
    d = np.genfromtxt(def_csv_file, delimiter=',',skip_header=2)

    # Offset the positions to the iso centre
    d[:,0:3] = d[:,0:3]-iso

    # Adjust the position for the pixel spacing
    d[:,0:3] = d[:,0:3]*px_spacing

    # Compute the distances to the center
    dists_from_iso = np.sqrt(np.power(d[:,0:1],2)+np.power(d[:,1:2],2)+np.power(d[:,2:3],2))

    # Compute each vector's magnitude
    mags = np.sqrt(np.power(d[:,3:4],2)+np.power(d[:,4:5],2)+np.power(d[:,5:6],2))

    mag_max = np.max(mags)
    mag_min = np.min(mags)
    mag_mean = np.mean(mags)
    mag_std = np.std(mags)
    logger.info('Max magnitude: ' + str(mag_max))
    logger.info('Min magnitude: ' + str(mag_min))
    logger.info('Mean magnitude: ' + str(mag_mean))
    logger.info('Std magnitude: ' + str(mag_std))


    output_file = file_base + "_Analysis.txt"
    f = open(output_file, "w")
    f.write('Max magnitude: ' + str(mag_max) + '\n')
    f.write('Min magnitude: ' + str(mag_min) + '\n')
    f.write('Mean magnitude: ' + str(mag_mean) + '\n')
    f.write('Std magnitude: ' + str(mag_std) + '\n')
    f.close()

    # Scatter plot
    plt.scatter(dists_from_iso, mags)
    plt.xlabel("Distance from ISO (mm)")
    plt.ylabel("Total Distortion (mm)")
    plt.show()

    logger.info('Analysis complete')

    return output_file

# Runs when this script is executed directly from the commmand line
if __name__ == "__main__":

    def_field="./CT-maskedDefField.csv"

    analysis(def_field, "analysis.txt", [119, 100, 35], px_spacing = [1.195312,1.195312,3])
