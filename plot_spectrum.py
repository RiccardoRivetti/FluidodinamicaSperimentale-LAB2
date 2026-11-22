import numpy as np
import matplotlib.pyplot as plt
import argparse
import pandas as pd
from pathlib import Path
import re

colors_poli = ["#102C53", "#0BA4FF", "#67B2C6"]

def read_header(filename):
    with open(filename) as f:
        line = f.readline()
    pairs = re.findall(r"([^;=\s]+)\s*=\s*([^;]+);?", line)
    return {k: float(v) for k, v in pairs}

def get_filename(folder, z, extention):
    return folder + f"/10deg_Z{z:.1f}" + extention

def import_wake_velocity(folder, heights):
    t_list = []
    V_list = []

    for z in heights:
        filename = get_filename(folder,z,".dat")
        filename = Path(filename)
        header = read_header(filename)

        f_sampling = header["Fs[Hz]"]
        V_wake = np.loadtxt(filename,skiprows=1)
        
        samples = len(V_wake)
        t_end = samples / f_sampling
        time = np.linspace(0,t_end,samples)

        t_list.append(time)
        V_list.append(V_wake)

    return np.column_stack(t_list), np.column_stack(V_list)

def import_wake_spectrum(folder, heights):
    f_list = []
    amp_list = []
    k_list = []
    Ek_list = []
    K41_list = []

    for z in heights:
        filename = get_filename(folder,z,".npz")
        filename = Path(filename)

        data = np.load(filename)

        f_list.append(data["f"])
        amp_list.append(data["amp"])
        k_list.append(data["k"])
        Ek_list.append(data["Ek"])
        K41_list.append(data["K41"])

    f = np.column_stack(f_list)
    amp = np.column_stack(amp_list)
    k = np.column_stack(k_list)
    Ek = np.column_stack(Ek_list)
    K41 = np.column_stack(K41_list)

    return f, amp, k, Ek, K41

def plot_wake_velocity(heights, time, V_wake, show_plot):
    fig, ax = plt.subplots()

    for i in range(len(heights)):
        ax.plot(time[:,i],V_wake[:,i],label=f"z = {heights[i]:.1f} mm",color=colors_poli[i],linewidth=1)

    plt.xlim((0,5))
    plt.ylim((10,20))

    plt.grid(True,linestyle="--",alpha=0.4)
    plt.legend(fontsize=12,loc="lower left")
    plt.xlabel("Time [s]",fontsize=14)
    plt.ylabel("$V_{wake}$ [m/s]",fontsize=14)
    plt.title("AoA = 10 deg",fontsize=14,loc="right")

    plt.savefig(f"./Figures/wake_velocity.png", dpi=300, bbox_inches="tight")
    plt.savefig(f"./Figures/wake_velocity.pdf", bbox_inches="tight")

    if show_plot:
        plt.show()

def plot_wake_spectrum(heights, frequency, amplitude, show_plot):
    fig, axs = plt.subplots(len(heights), 1, figsize=(8, 8), sharex=True)

    for i in range(len(heights)):
        axs[i].plot(frequency[:,i],amplitude[:,i],label=f"z = {heights[i]:.1f} mm",color=colors_poli[i],linewidth=1)

        axs[i].set_xlim((0,np.max(frequency[:,i])))
        axs[i].grid(True,linestyle="--",alpha=0.4)
        axs[i].legend(fontsize=12,loc="upper right")
        axs[i].set_ylabel("$|V_{wake}|$ [m/s]",fontsize=14)

    axs[0].set_title("AoA = 10 deg",fontsize=14,loc="right")
    axs[-1].set_xlabel("Frequency [Hz]",fontsize=14)

    plt.savefig(f"./Figures/wake_spectrum.png", dpi=300, bbox_inches="tight")
    plt.savefig(f"./Figures/wake_spectrum.pdf", bbox_inches="tight")

    if show_plot:
        plt.show()

def plot_energy_spectrum(k, Ek, K41, z, show_plot):
    fig, ax = plt.subplots()

    ax.loglog(k,Ek,label=f"Misura sperimentale",color=colors_poli[0],linewidth=1)
    ax.loglog(k,K41,label=f"Teoria K41",color=colors_poli[1],linewidth=2,linestyle="--")

    plt.xlim((1e1,1e4))
    plt.ylim((1e-7,1e-2))

    plt.grid(True,linestyle="--",alpha=0.4)
    plt.legend(fontsize=12,loc="lower left")
    plt.xlabel("$k$ [rad/m]",fontsize=14)
    plt.ylabel("$E(k)$ [m$^3$s$^{-2}$]",fontsize=14)
    plt.title(f"z = {z} mm",fontsize=14,loc="right")

    plt.savefig(f"./Figures/energy_spectrum.png", dpi=300, bbox_inches="tight")
    plt.savefig(f"./Figures/energy_spectrum.pdf", bbox_inches="tight")

    if show_plot:
        plt.show()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-z", type=float, nargs=3, metavar=("z1", "z2", "z3"),
                    default=(152.5, 170, 200), help="Vector of 3 heights to plot")
    ap.add_argument("--plot", action="store_true", help="Show plots")
    args = ap.parse_args()

    heights = args.z
    show_plot = args.plot

    velocity_folder = "./Data/hot_wire"
    spectrum_folder = "./Output/spectrum"

    # Plot velocity in time
    time, V_wake = import_wake_velocity(velocity_folder,heights)
    plot_wake_velocity(heights,time,V_wake,show_plot)

    # Plot spectrum
    frequency, amplitude, k, Ek, K41 = import_wake_spectrum(spectrum_folder,heights)
    plot_wake_spectrum(heights,frequency,amplitude,show_plot)

    # Plot energy spectrum
    z_idx = 0 # Select which z to plot the energy spectrum
    plot_energy_spectrum(k[:,z_idx], Ek[:,z_idx], K41[:,z_idx], heights[z_idx], show_plot)


if __name__ == "__main__":
    main()