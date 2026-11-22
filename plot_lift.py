import numpy as np
import matplotlib.pyplot as plt
import argparse

bluepoli1 = "#102C53"
bluepoli2 = "#0BA4FF"
bluepoli3 = "#67B2C6"

def import_measured_coeff(filename):
    data = np.loadtxt(filename,delimiter=",",skiprows=1)

    alpha = data[:,0]
    CL_mean = data[:,1]
    CL_unc = data[:,2]

    return alpha, CL_mean, CL_unc

def import_xfoil_data(filename):
    data = np.loadtxt(filename,delimiter=",",skiprows=1)

    alpha = data[:,0]
    CL = data[:,1]

    return alpha, CL

def plot_lift_coefficient(alpha, CL_mean, CL_unc, alpha_xfoil, CL_xfoil, show_plot):
    fig, ax = plt.subplots()

    ax.plot(alpha,CL_mean,label="Misura sperimentale",
                marker="s",color=bluepoli1,zorder=2,clip_on=False)
    ax.fill_between(alpha, CL_mean-CL_unc, CL_mean+CL_unc, color=bluepoli1, alpha=.5,
                    linewidth=0, label="I.C. 95%", zorder=1)
    ax.plot(alpha_xfoil,CL_xfoil,label="xfoil",color=bluepoli2,linestyle="--",zorder=0)

    plt.xlim((np.min(alpha),np.max(alpha)))

    plt.grid(True,linestyle="--",alpha=0.4)
    plt.legend(fontsize=12,loc="upper left")
    plt.xlabel(r"$\alpha$ [deg]",fontsize=14)
    plt.ylabel("$C_L$ [-]",fontsize=14)

    plt.savefig(f"./Figures/CL_alpha.png", dpi=300, bbox_inches="tight")
    plt.savefig(f"./Figures/CL_alpha.pdf", bbox_inches="tight")

    if show_plot:
        plt.show()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_file", help="Path of the input data file")
    ap.add_argument("--plot", action="store_true", help="Show plots")
    args = ap.parse_args()

    input_file = args.input_file
    show_plot  = args.plot

    # Import measured and xfoil CL
    alpha, CL_mean, CL_unc = import_measured_coeff(input_file)
    alpha_xfoil, CL_xfoil = import_xfoil_data("./xfoil/polar_xfoil.csv")

    # Plot lift coefficient
    plot_lift_coefficient(alpha,CL_mean,CL_unc,alpha_xfoil,CL_xfoil,show_plot)

if __name__ == "__main__":
    main()