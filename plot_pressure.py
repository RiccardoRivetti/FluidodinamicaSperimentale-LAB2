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

def import_coordinates(filename):
    coords = np.loadtxt(filename,delimiter=",",skiprows=1)
    x  = coords[:,0]
    y  = coords[:,1]

    return x, y

def split_surfaces(x):
    up  = x[:8]
    low = x[8:]

    return up, low

def draw_arrow(ax, x0, y0, x_airfoil, y_airfoil, magnitude):
    # Divide upper and lower surface and find tap position
    idx_le = np.where((x_airfoil == 0) & (y_airfoil == 0))[0][0]
    if y0 >= 0:
        xx = x_airfoil[:idx_le]
        yy = y_airfoil[:idx_le]
        idx = np.searchsorted(-xx, -x0)
    else:
        xx = x_airfoil[idx_le:]
        yy = y_airfoil[idx_le:]
        idx = np.searchsorted(xx, x0)
    
    # Compute the normal versor
    xx1, xx2 = xx[idx-1], xx[idx]
    yy1, yy2 = yy[idx-1], yy[idx]
    dx, dy = xx2 - xx1, yy2 - yy1

    L = np.hypot(dx, dy)
    nx, ny = dy/L, -dx/L

    # Compute segment midpoint
    xm, ym = (xx1+xx2)/2, (yy1+yy2)/2

    # Compute final point
    scale = 0.5
    ux, uy = -magnitude * nx * scale, -magnitude * ny * scale

    # Orient vector
    if magnitude > 0:
        x_start, y_start = xm - ux, ym - uy  # shift the tail outside, head lands on the surface
    else:
        x_start, y_start = xm, ym            # tail on the surface, head outside

    # Draw vector
    ax.quiver(x_start, y_start, ux, uy, angles="xy", scale_units="xy", scale=1, color=bluepoli2, width=0.005, zorder=0)
    return (x_start, y_start), (x_start + ux, y_start + uy)

def plot_pressure_coefficient(x_taps, Cp_mean, Cp_unc, x_xfoil, Cp_xfoil, alpha, show_plot):
    x_up, x_low = split_surfaces(x_taps)
    Cp_mean_up, Cp_mean_low = split_surfaces(Cp_mean)
    Cp_unc_up, Cp_unc_low = split_surfaces(Cp_unc)

    fig, ax = plt.subplots()
    
    ax.errorbar(x_up,Cp_mean_up,yerr=Cp_unc_up,label="Dorso",marker="s",color=bluepoli1,capsize=3,zorder=2)
    ax.errorbar(x_low,Cp_mean_low,yerr=Cp_unc_low,label="Ventre",marker="s",color=bluepoli2,capsize=3,zorder=1)
    ax.plot(x_xfoil,Cp_xfoil,label="xfoil",color=bluepoli3,linestyle="--",zorder=0)

    ax.invert_yaxis()

    plt.grid(True,linestyle="--",alpha=0.4)
    plt.xlabel("x/c [-]",fontsize=14)
    plt.ylabel("$C_p$ [-]",fontsize=14)
    plt.title(f"AoA = {alpha} deg",fontsize=14,loc="right")

    handles, labels = ax.get_legend_handles_labels()
    order = [1,2,0]
    plt.legend([handles[i] for i in order], [labels[i] for i in order], fontsize=14)

    plt.savefig(f"./Figures/Cp_AoA_{alpha}.png", dpi=300, bbox_inches="tight")
    plt.savefig(f"./Figures/Cp_AoA_{alpha}.pdf", bbox_inches="tight")

    if show_plot:
        plt.show()

def plot_airfoil_pressure(x_airfoil, y_airfoil, x_taps, y_taps, Cp_mean, alpha, show_plot):
    fig, ax = plt.subplots()

    # Plot airfoil
    ax.plot(x_airfoil,y_airfoil,color=bluepoli1,zorder=1,linewidth=2)

    # Plot arrows
    pts = [] # Initialize points to dinamically adjust axes limits
    for i in range(len(Cp_mean)):
        tail, head = draw_arrow(ax,x_taps[i],y_taps[i],x_airfoil,y_airfoil,Cp_mean[i])
        pts += [tail, head]
    
    # Dynamically set limits so that arrows don't go outside of the graph
    ax.update_datalim(pts)
    ax.autoscale_view()
    ax.set_aspect("equal")

    plt.grid(True,linestyle="--",alpha=0.4)
    plt.xlabel("x/c [-]",fontsize=14)
    plt.ylabel("y/c [-]",fontsize=14)
    plt.title(f"AoA = {alpha} deg",fontsize=14,loc="right")

    plt.savefig(f"./Figures/airfoil_pressure_AoA_{alpha}.png", dpi=300, bbox_inches="tight")
    plt.savefig(f"./Figures/airfoil_pressure_AoA_{alpha}.pdf", bbox_inches="tight")

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
    x_taps, y_taps = import_coordinates("./Data/taps_positions.csv")

    # Import airfoil coordinates
    x_airfoil, y_airfoil = import_coordinates("./Data/NACA23012.csv")

    # Plot pressure coefficient
    plot_pressure_coefficient(x_taps,Cp_mean,Cp_unc,x_xfoil,Cp_xfoil,alpha,show_plot)
    plot_airfoil_pressure(x_airfoil,y_airfoil,x_taps,y_taps,Cp_mean,alpha,show_plot)
    

if __name__ == "__main__":
    main()