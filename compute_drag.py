import numpy as np
import argparse
from pathlib import Path
import re
from experimental_setup import *

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
    V_wt = []
    f_s = []

    v_hw_mean = []
    v_hw_std = []
    I_u = []

    for path in sorted(folder.glob("*.dat")):
        header = read_header(path)
        z.append(header["Z[mm]"])
        V_wt.append(header["Vgall[m/s]"])
        f_s.append(header["Fs[Hz]"])

        v_hw  = np.loadtxt(path,skiprows=1)
        v_hw_mean.append(np.mean(v_hw))
        v_hw_std.append(np.std(v_hw))
        I_u.append(get_turbulence_intensity(np.std(v_hw),header["Vgall[m/s]"]))

    return z, V_wt, f_s, v_hw_mean, v_hw_std, I_u

def export_wake_data(filename, z, V_wt, f_s, v_hw_mean, v_hw_std, I_u):
    data = np.column_stack((z, V_wt, f_s, v_hw_mean, v_hw_std, I_u))
    header = "z,V_wt,f_s,v_hw_mean,v_hw_std,I_u"

    np.savetxt(filename,data,fmt="%.6e",delimiter=",",header=header,comments="")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_folder", help="Path of the input data folder")
    args = ap.parse_args()

    input_folder = args.input_folder

    output_folder = "./Output"

    # Import data from files
    z, V_wt, f_s, v_hw_mean, v_hw_std, I_u = import_data(input_folder)

    # Export wake data
    export_wake_data(output_folder+"/wake.csv", z, V_wt, f_s, v_hw_mean, v_hw_std, I_u)
    print(f"Wrote wake file in {output_folder}")

if __name__ == "__main__":
    main()


