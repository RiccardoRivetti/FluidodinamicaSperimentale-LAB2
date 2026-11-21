import numpy as np
import argparse
from pathlib import Path
import re
from scipy.signal import welch

def read_header(filename):
    with open(filename) as f:
        line = f.readline()
    pairs = re.findall(r"([^;=\s]+)\s*=\s*([^;]+);?", line)
    return {k: float(v) for k, v in pairs}

def import_data(filename):
    filename = Path(filename)
    header = read_header(filename)

    z = header["Z[mm]"]
    f_sampling = header["Fs[Hz]"]
    V_wake = np.loadtxt(filename,skiprows=1)

    samples = len(V_wake)
    t_end = samples / f_sampling
    time = np.linspace(0,t_end,samples)

    return z, f_sampling, time, V_wake

def get_spectrum(V, f_s):
    x = np.asarray(V, dtype=float)
    N = len(x)
    dt = 1 / f_s

    X = np.fft.rfft(x - x.mean()) # remove the mean (DC) first
    f = np.fft.rfftfreq(N, d=dt) # frequency axis in Hz
    amp = 2 * np.abs(X) / N # single-sided amplitude spectrum
    amp[0] /= 2 # DC bin is not doubled (irrelevant if you removed the mean)

    return f, amp

def get_energy_spectrum(V, f_s, nseg=2**13):
    V_bar = V.mean()
    vp = V - V_bar

    f, Pxx = welch(vp, fs=f_s, window="hann", nperseg=nseg, noverlap=nseg // 2,
               detrend="constant", scaling="density")

    k = 2 * np.pi * f / V_bar
    Ek = Pxx * V_bar / (2 * np.pi)

    return k[1:], Ek[1:]

def get_K41(k, Ek, k_fit=(100,1000), C=0.49):
    # Estimate epsilon
    mask = (k >= k_fit[0]) & (k <= k_fit[1])
    eps_loc = (Ek[mask] * k[mask] ** (5 / 3) / C) ** 1.5
    epsilon = eps_loc.mean()

    # Return K41
    return C * epsilon ** (2/3) * k ** (-5/3)

def export_spectrum_data(filename,f,amp):
    data = np.column_stack((f,amp))
    header = "Frequency[Hz],Amplitude[m/s]"

    np.savetxt(filename,data,fmt="%.6e",delimiter=",",header=header,comments="")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_file", help="Path of the input data file")
    args = ap.parse_args()

    input_file = args.input_file

    output_folder = "./Output/spectrum"

    # Extract data
    z, f_sampling, time, V_wake = import_data(input_file)

    # Compute spectrum
    frequency, amplitude = get_spectrum(V_wake, f_sampling)

    # Compute energy spectrum in spatial frequencies domain and K41 theory
    k, Ek = get_energy_spectrum(V_wake, f_sampling)
    K41 = get_K41(k, Ek)

    # Export data
    filename = output_folder + "/10deg_Z" + str(z) + ".npz"
    # export_spectrum_data(filename, frequency, amplitude)
    np.savez(filename, f=frequency, amp=amplitude, k=k, Ek=Ek, K41=K41)
    print(f"Wrote spectrum file in {output_folder}")
    
if __name__ == "__main__":
    main()