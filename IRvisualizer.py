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
    USE DISCOURAGED DUE TO HARDCODED METADATA CUTTING
    """
    xydata = pd.read_csv(filename, engine="python", names=["X", "Y"], skiprows=19, skipfooter=40)
    return xydata


def import_irdata_from_csv(filename):
    """
    Read csv and identify start and end of dataset by "XYDATA" and "##### Extended Information" keywords
    """
    xydata = pd.read_csv(filename, names=["X", "Y"])
    data_start = xydata.index[xydata["X"] == "XYDATA"].tolist()
    data_end = xydata.index[xydata["X"] == "##### Extended Information"].tolist()
    xydata = xydata.iloc[data_start[0] + 1: data_end[0], :]
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
    fig, axs = plt.subplots(1, 1)
    axs.plot(df["X"], df["Y"])
    axs.set_xlim(xlim_start, xlim_end)
    axs.set_ylim(ylim_start, ylim_end)
    axs.set_xlabel('wavenumber [$\mathregular{cm^{-1}]}$')
    axs.set_ylabel('transmission [a.u.]')
    axs.grid(True)
    axs.set_title(filename)
    fig.tight_layout()
    plt.draw()


# MAIN
# defaults for plot if no flag -x or -y is given
x_start = 4000  # default x-limit
x_end = 500     # default x-limit
y_start = None  # default y-limit
y_end = None    # default y-limit
j, k = False, False  # auxiliary variable to check if -x or -y was given

if __name__ == '__main__':
    # check if any argument was given
    arguments = sys.argv  # create a copy of sys.argv (since arguments will be modified)
    if len(arguments) == 1:
        sys.exit("ERROR: No argument given. Please give at least one csv file with IR data.")
    print(arguments, "\n")
    # check if -x and -y flags were given
    for i in range(0, len(arguments)):
        if "-x" in arguments[i]:
            x_start = int(arguments[i+1])
            x_end = int(arguments[i+2])
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

    # print(arguments, "\n")
    print("Plotting all spectra with x limit {} to {}".format(x_start, x_end))
    print("Plotting all spectra with y limit {} to {}\n".format(y_start, y_end))
    # import csv to df
    importedData = {}
    normalizedData = {}
    for i in range(0, len(arguments)-1):  # -2 to remove script name argument and not walk past array length
        # print("i:",i)
        file = arguments[i+1]        # +1 to omit sys.argv[0] which is script name
        if ".csv" not in file:
            print("ERROR: Encountered invalid file type for {} (only .csv allowed). Skipping this file.".format(file))
        elif "_normalized.csv" in file:
            print("Skipping previously processed file {}".format(file))
        else:
            print("Importing {}...".format(file))
            importedData[file] = import_irdata_from_csv(file)
            # normalize Y values of df
            normalizedData[file] = normalize_y(importedData[file])
            print("Normalized data for {}. Output:\n {}\n".format(file,normalizedData[file]))
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
