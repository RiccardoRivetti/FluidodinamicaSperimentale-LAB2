import numpy as np
import argparse
from pathlib import Path
from experimental_setup import *

K_WT = 1.159701 # Calibration constant of wind tunnel
pressure_transducer = PressureTransducer("HD4V8T",1000,0.05)

def import_data(filename):
    # Import data
    data = np.loadtxt(filename,delimiter=",",skiprows=1)
    data = data[np.argsort(data[:,-1])]

    # Extract list of angles
    angles = np.unique(data[:,-1])

    return data, angles

def import_taps_coordinates(filename):
    coords = np.loadtxt(filename,delimiter=",",skiprows=1)
    x_up  = coords[0:8,0]
    x_low = coords[8:,0]
    y_up  = coords[0:8,1]
    y_low = coords[8:,1]

    return x_up, x_low, y_up, y_low

def get_dynamic_pressure(signal):
    return signal*K_WT

def divide_surfaces(Cp):
    upper = Cp[0:8]
    lower = Cp[8:]

    return upper, lower

def get_lift_coefficient(measures, x_up, x_low):
    n_meas = len(measures[:,0])
    CL = np.zeros((n_meas,16))
    q  = np.zeros(n_meas)

    for i in range(n_meas):
        q[i] = get_dynamic_pressure(measures[i,16])
        Cp = measures[i,0:16] / q[i]

        # Divide in upper and lower surface
        upper, lower = divide_surfaces(Cp)


    return CL, q

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_file", help="Path of the input data file")
    args = ap.parse_args()

    input_file = args.input_file

    # Output path
    output_folder = "./Output"
    
    # Import data and list of angles
    DATA, angles = import_data(input_file)

    # Import pressure taps coordinates
    x_up, x_low, y_up, y_low = import_taps_coordinates("./Data/taps_positions.csv")

    # Loop for each angle
    for alpha in angles:
        # Select pressure data for specific angle
        measures = DATA[DATA[:,-1] == alpha]

        # Compute lift coefficients and dynamic pressures
        CL, q = get_lift_coefficient(measures,x_up,x_low)
    





if __name__ == "__main__":
    main()