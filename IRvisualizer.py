#!/usr/bin/env python

"""
Tool to normalize and visualize IR spectra from csv files
Takes the following arguments and flags:
-x <start> <end> (optional): x limits for the plot. Type int. Default is 4000, 500.
-y <start> <end> (optional): y limits for the plot. Type float. Default is automatic mode.
<file>.csv: csv file with IR spectral data. The number is arbitrary.
            If "*" is used, all csv files in the working directory are plotted
"""

import pandas as pd
import matplotlib.pyplot as plt
import sys


def legacy_import_data(filename):
    """
    Read a csv, skipping the first 19 rows (metadata) and the last 40 rows (extended metadata)
    FOR REFERENCE ONLY. USE DISCOURAGED DUE TO HARDCODED METADATA SLICING.
    """
    xydata = pd.read_csv(filename, engine="python", names=["X", "Y"], skiprows=19, skipfooter=40)
    return xydata


def import_irdata_from_csv(filename):
    """
    Read csv and identify start and end of dataset by "XYDATA" and "##### Extended Information" keywords
    """
    xydata = pd.read_csv(filename, names=["X", "Y"])
    data_start = xydata.index[xydata["X"] == "XYDATA"].item()
    data_end = xydata.index[xydata["X"] == "##### Extended Information"].item()
    xydata = xydata.iloc[data_start + 1: data_end, :]
    xydata.reset_index(inplace=True, drop=True)
    xydata = xydata.astype("float64")
    return xydata


def normalize_y(df):
    """
    Normalize the Y-values of pandas.DataFrame to a maximum of 1
    """
    df["Y"] = df["Y"] / df["Y"].max()
    return df


def plot_spectrum(df, filename, xlim_start, xlim_end, ylim_start, ylim_end):
    """
    Plot an IR spectrum from a pandas.DataFrame with "X" and "Y" columns
    """
    fig, axs = plt.subplots(1, 1)  # initialize a canvas with one figure which has one axis
    axs.plot(df["X"], df["Y"])  # plot the data
    # cut the plot according to user input
    axs.set_xlim(xlim_start, xlim_end)
    axs.set_ylim(ylim_start, ylim_end)
    # set informative labels
    axs.set_xlabel('wavenumber [$\mathregular{cm^{-1}]}$')  # matplotlib can interpret this LateX expression
    axs.set_ylabel('transmission [a.u.]')
    axs.grid(True)  # show a grid to help guide the viewer's eye
    axs.set_title(filename)  # set a title from the filename of the input data
    fig.tight_layout()  # a standard option for matplotlib
    plt.draw()


# MAIN
# defaults for plot if no flag -x or -y is given
x_start = 4000  # default x-limit
x_end = 500     # default x-limit
y_start = None  # default y-limit
y_end = None    # default y-limit
j, k = False, False  # auxiliary variable to check if -x or -y was given

if __name__ == '__main__':
    # deal with the arguments passed from command line
    arguments = sys.argv  # create a copy of sys.argv (since arguments will be modified)
    if len(arguments) == 1:
        sys.exit("ERROR: No argument given. Please give at least one csv file with IR data.")
    print(arguments, "\n")
    # check if -x and -y flags were given
    for i in range(0, len(arguments)):
        if "-x" in arguments[i]:
            x_start = int(arguments[i+1])  # the argument after "-x"
            x_end = int(arguments[i+2])  # the 2nd argument after "-x"
            j = i
        if "-y" in arguments[i]:
            y_start = float(arguments[i+1])
            y_end = float(arguments[i+2])
            k = i
    # if the -x and/or -y flags were given, delete them and the following two values from sys.argv
    if j:
        del arguments[j:j + 3]
        if k:
            del arguments[k-3:k]
    elif k:
        del arguments[k:k + 3]

    # Print some information to interactive output
    print("Plotting all spectra with x limit {} to {}".format(x_start, x_end))
    print("Plotting all spectra with y limit {} to {}\n".format(y_start, y_end))

    # Process spectra in batch
    importedData = {}
    normalizedData = {}
    # iterate all filenames given when this script was called
    for i in range(1, len(arguments)):  # start at 1 since arguments[0] is just the name of the script
        file = arguments[i]  # for convenience
        if ".csv" not in file:
            print("WARNING: Encountered invalid file type for {} (only .csv allowed). Skipping this file.".format(file))
        elif "_normalized.csv" in file:
            print("Skipping previously processed file {}".format(file))
        else:
            print("Importing {}...".format(file))
            importedData[file] = import_irdata_from_csv(file)
            # normalize Y values of df
            normalizedData[file] = normalize_y(importedData[file])
            print("Normalized data for {}. Output:\n {}\n".format(file, normalizedData[file]))
            # plot the spectra
            plot_spectrum(normalizedData[file], file, x_start, x_end, y_start, y_end)
            print("Plotted spectra for {}.\n".format(file))
            # save to csv
            newfile = file.strip(".csv")+"_normalized.csv"
            normalizedData[file].to_csv(newfile, header=False, index=False)
            print("Saved normalized data to file {}".format(newfile))
    print("All spectra processed. Exiting... (close all plots to exit)")
    # ensure that all plots stay open
    plt.show()
