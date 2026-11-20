import numpy as np
import matplotlib.pyplot as plt
import argparse
import pandas as pd

bluepoli1 = "#102C53"
bluepoli2 = "#0BA4FF"
bluepoli3 = "#67B2C6"

def import_data(filename):
    return pd.read_csv(filename)

def plot_wake_velocity(z,v_hw,show_plot):
    fig, ax = plt.subplots()

    ax.plot(z,v_hw,label="Misura sperimentale",marker="s",color=bluepoli1,clip_on=False)

    plt.grid(True,linestyle="--",alpha=0.4)
    # plt.legend(fontsize=12,loc="upper left")
    # plt.xlabel("$V_wake$ [m/s] [deg]",fontsize=14)
    # plt.ylabel("$z$ [mm]",fontsize=14)

    if show_plot:
        plt.show()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_file", help="Path of the input data file")
    ap.add_argument("--plot", action="store_true", help="Show plots")
    args = ap.parse_args()

    input_file = args.input_file
    show_plot  = args.plot

    # Import data
    DATA = import_data(input_file)
    print(DATA)
    # print(DATA["z"].sort_values().to_numpy())

    # Plot wake velocity and turbulence intensity
    plot_wake_velocity(DATA["z"],DATA["v_hw_mean"],show_plot)

if __name__ == "__main__":
    main()