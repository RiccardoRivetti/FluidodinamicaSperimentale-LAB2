import numpy as np
import argparse
from experimental_setup import *

# Define the experiment parameters
K_WT = 1.159701 # Calibration constant of wind tunnel
pressure_transducer = PressureTransducer("HD4V8T",1000,0.05)

test_wing = Wing("NACA23012",0.100,0.293,0.12,4.232,3.00174e-4)
test_section = TestSection(1,0.3,0.45,10)

def import_data(filename):
    # Import data
    data = np.loadtxt(filename,delimiter=",",skiprows=1)
    data = data[np.argsort(data[:,-1])]

    # Extract list of angles
    angles = np.unique(data[:,-1])

    return data, angles

def get_dynamic_pressure(signal):
    return signal*K_WT

def get_pressure_coefficients(measures):
    n_meas = len(measures[:,0])
    Cp = np.zeros((n_meas,16))
    q  = np.zeros(n_meas)

    for i in range(n_meas):
        q[i] = get_dynamic_pressure(measures[i,16])
        Cp[i,:] = measures[i,0:16] / q[i]

    return Cp, q

def get_Cp_stats(Cp,q):
    # Compute mean
    Cp_mean = Cp.mean(axis=0)

    # Compute type A uncertanty
    N = Cp.shape[0]
    u_A = Cp.std(axis=0, ddof=1) / np.sqrt(N)

    # Compute type B uncertanty
    accuracy = pressure_transducer.accuracy * pressure_transducer.full_scale
    u_p = accuracy / np.sqrt(3) # Pressure tranducer uncertanty (rectangular distribution)

    q_mean = q.mean()
    u_B = (u_p / q_mean) * np.sqrt(1 + (K_WT * Cp_mean)**2)

    # Combine uncertanties
    u_combined = np.sqrt(u_A**2 + u_B**2)
    Cp_unc = 2 * u_combined # 95% confidence interval with k=2

    return Cp_mean, Cp_unc, u_A, u_B

def angle_to_name(alpha):
    return f"{alpha:g}".replace("-", "m").replace(".", "_")

def get_filename(output_folder, alpha):
    return output_folder + "/Cp_aoa_" + angle_to_name(alpha) + ".csv"

def write_Cp_file(output_folder, alpha, Cp_mean, Cp_unc, u_A, u_B):
    filename = get_filename(output_folder,alpha)

    results = np.column_stack((Cp_mean,Cp_unc,u_A,u_B))
    header = "Cp_mean,Cp_unc,u_A,u_B"
    np.savetxt(filename,results,delimiter=",",fmt="%.6e",header=header,comments="")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_file", help="Path of the input data file")
    args = ap.parse_args()

    input_file = args.input_file

    # Output path
    output_folder = "./Output/Cp"

    # Import data and list of angles
    DATA, angles = import_data(input_file)

    # Loop for each angle
    for alpha in angles:
        # Select pressure data for specific angle
        measures = DATA[DATA[:,-1] == alpha]

        # Compute pressure coefficients and dynamic pressures
        Cp, q = get_pressure_coefficients(measures)

        # Compute pressure coefficients mean and uncertanty
        Cp_mean, Cp_unc, u_A, u_B = get_Cp_stats(Cp,q)

        # Write data in file
        write_Cp_file(output_folder,alpha,Cp_mean,Cp_unc,u_A,u_B)
        print(f"Wrote file for AoA = {alpha} in {output_folder}")

if __name__ == "__main__":
    main()