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

def get_trapz_weights(coords):
    return np.trapezoid(np.eye(len(coords)), coords)

def get_lift_coefficient(measures, x_up, x_low):
    n_meas = len(measures[:,0])
    CL = np.zeros(n_meas)
    q  = np.zeros(n_meas)

    for i in range(n_meas):
        q[i] = get_dynamic_pressure(measures[i,16])
        Cp = measures[i,0:16] / q[i]

        # Divide in upper and lower surface
        Cp_up, Cp_low = divide_surfaces(Cp)    

        # Compute lift coefficient
        CL[i] = -np.trapezoid(Cp_up, x_up) + np.trapezoid(Cp_low, x_low)

    return CL, q

def get_coefficient_stats(coeff,q,S_weights):
    # Compute mean
    coeff_mean = coeff.mean(axis=0)

    # Compute type A uncertanty
    N = coeff.shape[0]
    u_A = coeff.std(axis=0, ddof=1) / np.sqrt(N)

    # Compute type B uncertanty
    accuracy = pressure_transducer.accuracy * pressure_transducer.full_scale
    u_p = accuracy / np.sqrt(3) # Pressure tranducer uncertanty (rectangular distribution)

    q_mean = q.mean()
    u_B = (u_p / q_mean) * np.sqrt(S_weights + (K_WT * coeff_mean)**2)

    # Combine uncertanties
    u_combined = np.sqrt(u_A**2 + u_B**2)
    coeff_unc = 2 * u_combined # 95% confidence interval with k=2

    return coeff_mean, coeff_unc, u_A, u_B

def write_coefficient_file(filename,matrix):
    header = "Alpha,Mean,Unc,u_A,u_B"
    np.savetxt(filename,matrix,delimiter=",",fmt="%.6e",header=header,comments="")

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

    # Initialize coefficients matrix
    CL_MATRIX = np.zeros((len(angles),5))
    CL_MATRIX[:,0] = angles
    i = 0

    # Loop for each angle
    for alpha in angles:
        # Select pressure data for specific angle
        measures = DATA[DATA[:,-1] == alpha]

        # Compute sum of trapezoid weights
        w = np.concatenate([-get_trapz_weights(x_up),  get_trapz_weights(x_low)])
        S = w.sum()

        # Compute coefficients and dynamic pressures
        CL, q = get_lift_coefficient(measures,x_up,x_low)

        # Compute coefficient mean and uncertanty
        CL_mean, CL_unc, CL_u_A, CL_u_B = get_coefficient_stats(CL,q,S)

        # Insert in data matrix
        CL_MATRIX[i,1:] = [CL_mean, CL_unc, CL_u_A, CL_u_B]
        i += 1

    # Write results in files
    write_coefficient_file(output_folder+"/CL.csv",CL_MATRIX)
    print(f"Wrote CL file in {output_folder}")

if __name__ == "__main__":
    main()