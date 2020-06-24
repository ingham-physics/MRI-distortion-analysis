#!/usr/bin/env python3

import os
import subprocess
from datetime import datetime

import SimpleITK as sitk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

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
        df = sitk.ReadImage(def_file)
        px_spacing = df.GetSpacing()

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

    display_string = 'Max mag: {:.5f}\n'.format(mag_max)
    display_string += 'Min mag: {:.5f}\n'.format(mag_min)
    display_string += 'Mean mag: {:.5f}\n'.format(mag_mean)
    display_string += 'Std mag: {:.5f}\n'.format(mag_std)

    # Scatter plot
    plt.ion() # enables interactive mode
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(16, 6))
    sns.distplot(mags, kde = False, ax=ax2)
    sns.scatterplot([m[0] for m in dists_from_iso], [m[0] for m in mags], ax=ax1)

    ax1.set(xlabel='Distance from ISO (mm)', ylabel='Total Distortion (mm)')
    ax2.set(xlabel='Distortion (mm)', ylabel='Frequency')
    
    now = datetime.now()
    title = "MRI Distortion QA: {0}".format(now.strftime("%d/%m/%Y, %H:%M:%S"))
    plt.suptitle(title) 
    
    plt.figtext(0.15,0.7, display_string)
    plt.show()

    plot_file = file_base + "_plot.png"
    fig.savefig(plot_file)

    logger.info('Analysis complete')

    return output_file

# Runs when this script is executed directly from the commmand line
if __name__ == "__main__":

    def_field="./CT-maskedDefField.csv"

    perform_analysis(def_field, ".", [119, 100, 35], px_spacing = [1.195312,1.195312,3])
    input("Press Enter to continue...")
