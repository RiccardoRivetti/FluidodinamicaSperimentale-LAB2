import numpy as np
import argparse
from pathlib import Path
import re
from experimental_setup import *

test_wing = Wing("NACA23012",0.100,0.293,0.12,4.232,3.00174e-4)
test_section = TestSection(1,0.3,0.45,10)

def read_header(filename):
    with open(filename) as f:
        line = f.readline()
    pairs = re.findall(r"([^;=\s]+)\s*=\s*([^;]+);?", line)
    return {k: float(v) for k, v in pairs}

def get_turbulence_intensity(sigma,u):
    return sigma / u

def import_data(folder):
    folder = Path(folder)

    z = []
    f_s = []

    v_hw_mean = []
    v_hw_std = []
    I_u = []

    for path in sorted(folder.glob("*.dat")):
        header = read_header(path)
        z.append(header["Z[mm]"])
        f_s.append(header["Fs[Hz]"])

        v_hw  = np.loadtxt(path,skiprows=1)
        v_hw_mean.append(np.mean(v_hw))
        v_hw_std.append(np.std(v_hw))
        I_u.append(get_turbulence_intensity(np.std(v_hw),header["Vgall[m/s]"]))

    return z, f_s, v_hw_mean, v_hw_std, I_u

def import_xfoil_CD(filename, alpha):
    data = np.loadtxt(filename,delimiter=",",skiprows=1)
    return data[data[:,0]==alpha,2][0]

def export_wake_data(filename, z, V_wt, f_s, v_hw_mean, v_hw_std, I_u):
    data = np.column_stack((z, V_wt, f_s, v_hw_mean, v_hw_std, I_u))
    # data = data[data[:, 0].argsort()] # Sort in ascending z order
    header = "z,V_wt,f_s,v_hw_mean,v_hw_std,I_u"

    np.savetxt(filename,data,fmt="%.6e",delimiter=",",header=header,comments="")

def get_freestream(V, edge_frac=0.20, k=3):
    V = np.asarray(V, dtype=float)
    n = len(V)
    ne = max(3, int(edge_frac * n)) # How many edge point to consider

    # Initial estimation of freestream velocity
    edges = np.r_[V[:ne], V[-ne:]]
    V0 = np.median(edges) # Median is more robust
    sigma = max(np.std(edges), 0.002 * V0)      # Minimum std threshold: 0.2% di V0

    # Locate the wake 
    in_wake = (V0 - V) > k * sigma
    if not in_wake.any():
        raise ValueError("No wake detected")

    # 2 points margin for each side
    w = np.flatnonzero(in_wake) # Wake points idx
    lo, hi = max(w[0] - 2, 0), min(w[-1] + 2, n - 1) # No idx outside array
    outside = np.ones(n, bool); outside[lo:hi + 1] = False # Mask for points outside of the wake
    if outside.sum() < 4:
        raise ValueError("Too few points outside the wake")

    # Return the mean of the points outside of the wake
    return V[outside].mean()

def get_drag_coefficient(z,V_wt,V_wake):
    V_wake = np.asarray(V_wake, dtype=float)
    z = np.asarray(z, dtype=float)*0.001 # convert in meters
    
    integral = np.trapezoid((V_wake/V_wt) * (1-V_wake/V_wt),z)
    CD = 2/(test_wing.chord)*integral

    return CD

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_folder", help="Path of the input data folder")
    args = ap.parse_args()

    input_folder = args.input_folder

    xfoil_file = "./xfoil/polar_xfoil.csv"
    output_folder = "./Output"

    # Import data from files
    z, f_s, v_hw_mean, v_hw_std, I_u = import_data(input_folder)
    alpha = 10

    # Compute freestream wind tunnel velocity
    V_wt = get_freestream(v_hw_mean)

    # Compute drag
    CD_computed = get_drag_coefficient(z,V_wt,v_hw_mean)
    CD_xfoil = import_xfoil_CD(xfoil_file,alpha)
    print("-------------------------")
    print(f"AoA: {alpha} deg")
    print(f"Computed CD: {CD_computed:.5f}")
    print(f"Xfoil CD:    {CD_xfoil}")
    print("-------------------------")

    # Export wake data
    V_wt_array = V_wt*np.ones(len(z))
    export_wake_data(output_folder+"/wake.csv", z, V_wt_array, f_s, v_hw_mean, v_hw_std, I_u)
    print(f"Wrote wake file in {output_folder}")

if __name__ == "__main__":
    main()


