#!/usr/bin/python3
import argparse
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

parser = argparse.ArgumentParser(
    description='Create buffer position occupancy histogram.'
)
parser.add_argument('-i', '--info', dest='info')
parser.add_argument('-o', '--name', dest='name')
parser.add_argument('-l', '--log', dest='log', action='store_true')
parser.add_argument('-p', '--plot', dest='plot', action='store_true')
parser.add_argument('-s', '--show', dest='show', action='store_true')
args = parser.parse_args()

events_data = {
    "BASE": {
        # "DefineBufferType": 7,
        # "CreateBuffer": 7,
        # "DefinePackageType": 2,
        "InsertPackage": 672598,
        "RemovePackage": 672598,
        "UpdatePackage": 284799,
        "Clock": 162019,
        # "DefineStatusColor": 5,
    },

    "FETCH_S1": {
        # "DefineBufferType": 7,
        # "CreateBuffer": 7,
        # "DefinePackageType": 2,
        "InsertPackage": 672598,
        "RemovePackage": 672598,
        "UpdatePackage": 285969,
        "Clock": 804968,
        # "DefineStatusColor": 5,
    },

    "DECODE_S8": {
        # "DefineBufferType": 7,
        # "CreateBuffer": 7,
        # "DefinePackageType": 2,
        "InsertPackage": 672598,
        "RemovePackage": 672598,
        "UpdatePackage": 285335,
        "Clock": 191999,
        # "DefineStatusColor": 5,
    },

    "FU_S15 + URS_S13": {
        # "DefineBufferType": 7,
        # "CreateBuffer": 7,
        # "DefinePackageType": 2,
        "InsertPackage": 672598,
        "RemovePackage": 672598,
        "UpdatePackage": 285570,
        "Clock": 269320,
        # "DefineStatusColor": 5,
    },

    "ROB_S28": {
        # "DefineBufferType": 7,
        # "CreateBuffer": 7,
        # "DefinePackageType": 2,
        "InsertPackage": 672598,
        "RemovePackage": 672598,
        "UpdatePackage": 285365,
        "Clock": 251587,
        # "DefineStatusColor": 5,
    },

    "ROB_S1": {
        # "DefineBufferType": 7,
        # "CreateBuffer": 7,
        # "DefinePackageType": 2,
        "InsertPackage": 672598,
        "RemovePackage": 672598,
        "UpdatePackage": 285984,
        "Clock": 1091627,
        # "DefineStatusColor": 5,
    },

    "MEMORY": {
        # "DefineBufferType": 7,
        # "CreateBuffer": 7,
        # "DefinePackageType": 2,
        "InsertPackage": 672598,
        "RemovePackage": 672598,
        "UpdatePackage": 284473,
        "Clock": 347171,
        # "DefineStatusColor": 5,
    },

}

event_names = [
    # "DefineBufferType",
    # "CreateBuffer",
    # "DefinePackageType",
    "InsertPackage",
    "RemovePackage",
    "UpdatePackage",
    "Clock",
    # "DefineStatusColor",
]

# Create a color map
start = 0.0
stop = 1.0
number_of_lines= len(event_names)
cm_subsection = np.linspace(start, stop, number_of_lines) 
colors = [matplotlib.cm.viridis(x) for x in cm_subsection]

def format_decimal(x, pos):
    return '{:.0f}'.format(x)

formatter = matplotlib.ticker.FuncFormatter(format_decimal)

handles = [matplotlib.patches.Rectangle((0,0),1,1,color=c,ec="k") for c in colors]

if args.plot:
    num_plots = len(events_data)
    num_cols = 3
    num_rows = (num_plots // num_cols) + 1 if num_plots % num_cols != 0 else 0

    fig, axs = plt.subplots(num_rows, num_cols, figsize=(num_cols*3, num_rows*2.5), dpi=300)
    
    plt.subplots_adjust(wspace=0.2, hspace=0.2)

    ymax = 0.0
    for i, (buffer_name, data) in enumerate(events_data.items()):
        event_counts = data.values()
        for count in event_counts:
            if count > ymax:
                ymax = count

    for i, (buffer_name, data) in enumerate(events_data.items()):
        print(data)
        ax = axs[(i // num_cols) % num_rows, i % num_cols]       
        ax.grid(axis='y', linestyle='--', color='black')
        
        ax.set_title(
            buffer_name,
            fontsize=11,
            y=0.92, va="top", 
            # bbox=dict(facecolor='none', edgecolor='k')
        )

        ax.tick_params(axis='both', which='major', labelsize=11)
        ax.tick_params(axis='both', which='minor', labelsize=11)

        ax.set_ylim([0.0, ymax])

        if True:
            ticks = [ymax*n for n in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]]
            ax.set_yticks(ticks)
            ax.get_yaxis().set_major_formatter(formatter)
        
        if i % num_cols != 0:
            ax.set_yticklabels([])
        
        ax.set_aspect('auto')
        ax.set_xticks([])

        # Plot histogram on each subplot
        for idx, data_value in enumerate(data.values()):
            ax.bar(idx, data_value, width=1.0, align="center", ec="k", color=colors[idx])

    added_subplot = False
    c = 0
    for i in range(0, num_rows):
        for j in range(0, num_cols):
            c = c + 1
            if c > num_plots:
                if not added_subplot:
                    # plt.legend(handles, names, bbox_to_anchor=(1.2, 0.5), loc='center left')
                    axs[i, j].legend(handles, event_names, loc='center')
                    added_subplot = True
                axs[i, j].axis('off')


    plt.tight_layout()
    
    plt.savefig("plot.png" if args.name == None else "%s.png" % args.name)

    if args.show:
        plt.show()
