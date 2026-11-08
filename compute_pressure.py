import numpy as np
import argparse
from experimental_setup import *

K_WT = 1.159701 # Calibration constant of wind tunnel

def get_dynamic_pressure(signal):
    return signal*K_WT

def import_data(filename):
    # Import data
    data = np.loadtxt(filename,delimiter=",",skiprows=1)
    data = data[np.argsort(data[:,-1])]

    # Extract list of angles
    alpha = np.unique(data[:,-1])

    return data, alpha

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_file", help="Path of the input data file")
    args = ap.parse_args()

    input_file = args.input_file

    # Output path
    output_folder = "./Data/pressure"

    # Define the experiment parameters
    test_wing = Wing("NACA23012",0.100,0.293,0.12,4.232,3.00174e-4)
    test_section = TestSection(1,0.3,0.45,10)

    # Import data and list of alphas
    DATA, alpha = import_data(input_file)


if __name__ == "__main__":
    main()