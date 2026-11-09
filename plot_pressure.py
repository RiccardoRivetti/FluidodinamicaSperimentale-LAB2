import numpy as np
import matplotlib.pyplot as plt
import argparse

bluepoli1 = "#102C53"
bluepoli2 = "#0BA4FF"
bluepoli3 = "#67B2C6"

def angle_to_name(alpha):
    return f"{alpha:g}".replace("-", "m").replace(".", "_")

def get_input_files(folder,alpha):
    measures_file = folder + "/Cp_aoa_" + angle_to_name(alpha) + ".csv"
    xfoil_file = "./xfoil/Cp_aoa_" + angle_to_name(alpha) + "_xfoil.txt"
    return measures_file, xfoil_file

def import_measured_data(filename):
    data = np.loadtxt(filename,delimiter=",",skiprows=1)

    Cp_mean = data[:,0]
    Cp_unc  = data[:,1]

    return Cp_mean, Cp_unc

def import_xfoil_data(filename):
    data = np.loadtxt(filename,skiprows=1)

    x_xfoil  = data[:,0]
    Cp_xfoil = data[:,1]

    return x_xfoil, Cp_xfoil

def import_taps_coordinates(filename):
    coords = np.loadtxt(filename,delimiter=",",skiprows=1)
    x  = coords[:,0]
    y  = coords[:,1]

    return x, y

def split_surfaces(x):
    up  = x[:8]
    low = x[8:]

    return up, low

def plot_Cp(x_taps, Cp_mean, Cp_unc, x_xfoil, Cp_xfoil, alpha, show_plot):
    x_up, x_low = split_surfaces(x_taps)
    Cp_mean_up, Cp_mean_low = split_surfaces(Cp_mean)
    Cp_unc_up, Cp_unc_low = split_surfaces(Cp_unc)

    fig, ax = plt.subplots()
    
    ax.errorbar(x_up,Cp_mean_up,yerr=Cp_unc_up,label="Dorso",marker="s",color=bluepoli1,capsize=3,zorder=3)
    ax.errorbar(x_low,Cp_mean_low,yerr=Cp_unc_low,label="Ventre",marker="s",color=bluepoli2,capsize=3,zorder=2)
    ax.plot(x_xfoil,Cp_xfoil,label="xfoil",color=bluepoli3,linestyle="--",zorder=0)

    ax.invert_yaxis()

    plt.grid(True,linestyle="--",alpha=0.4)
    plt.legend(fontsize=12,loc="upper right")
    plt.xlabel("x/c [-]",fontsize=14)
    plt.ylabel("$C_p$ [-]",fontsize=14)
    plt.title(f"AoA = {alpha} deg",fontsize=14,loc="right")

    if show_plot:
        plt.show()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_folder", help="Path of the input data folder")
    ap.add_argument("-a", "--alpha", type=float, default=0, help="Angle of attack to plot")
    ap.add_argument("--plot", action="store_true", help="Show plots")
    args = ap.parse_args()

    input_folder = args.input_folder
    alpha = args.alpha
    show_plot = args.plot

    # Get input files name from angle of attack
    measures_file, xfoil_file = get_input_files(input_folder,alpha)

    # Extract measured and xfoil data
    Cp_mean, Cp_unc = import_measured_data(measures_file)
    x_xfoil, Cp_xfoil = import_xfoil_data(xfoil_file)

    # Import pressure taps coordinates
    x_taps, y_taps = import_taps_coordinates("./Data/taps_positions.csv")

    # Plot pressure coefficient
    plot_Cp(x_taps,Cp_mean,Cp_unc,x_xfoil,Cp_xfoil,alpha,show_plot)

if __name__ == "__main__":
    main()