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

    # Prepare Scatter plot
    plt.ion() # enables interactive mode
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(16, 6))

    # Compute for different distances from ISO
    dists = [None, 200, 100]
    colors = [[1,0,0],[0,1,0],[0,0,1]]
    for i, dist in enumerate(dists):

        print("Prepare for points within: {0}".format(dist))

        if dist:
            print(type(dists_from_iso))
            within_dists_from_iso = dists_from_iso[dists_from_iso < dist]
            print(type(within_dists_from_iso))
            within_mags = mags[dists_from_iso < dist]
        else:
            within_dists_from_iso = dists_from_iso
            within_mags = mags

        print(within_dists_from_iso.shape)
        print(within_mags.shape)

        
        mag_max = np.max(within_mags)
        mag_min = np.min(within_mags)
        mag_mean = np.mean(within_mags)
        mag_std = np.std(within_mags)
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

        sns.scatterplot(x = [m for m in within_dists_from_iso], y = [m for m in within_mags], ax=ax1)
        sns.distplot(within_mags, kde = False, ax=ax2, color=colors[i])

        ax1.set(xlabel='Distance from ISO (mm)', ylabel='Total Distortion (mm)')
        ax2.set(xlabel='Distortion (mm)', ylabel='Frequency')

    plt.table(cellText=[["test","test","test","test"], ["test","test","test","test"], ["test","test","test","test"]],
        rowLabels=["10cm from ISO", "20cm from ISO", "Total"],
        colLabels=["Mean", "Std", "Max", "Min"],
        cellLoc = 'right', rowLoc = 'center',
        loc='right', bbox=[.65,.05,.3,.5])
    
    now = datetime.now()
    title = "MRI Distortion QA: {0}".format(now.strftime("%d/%m/%Y, %H:%M:%S"))
    plt.suptitle(title) 
    
    plt.show()

    plot_file = file_base + "_plot.png"
    fig.savefig(plot_file)

    logger.info('Analysis complete')

    return output_file

# Runs when this script is executed directly from the commmand line
if __name__ == "__main__":

    def_field="../test/data/deform/GT.csv"

    perform_analysis(def_field, ".", [119, 100, 35], px_spacing = [1.195312,1.195312,3])
    input("Press Enter to continue...")
