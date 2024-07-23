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

timing_data = {
    'BASE': {
        'processing_time': {'value': 9088.348, 'unit': 'seconds'},
         'events/seconds': 197.180, 
         'cycles/seconds': 17.827 
    },

    'FETCH_S1': {
        'processing_time': {'value': 10199.102, 'unit': 'seconds'},
         'events/seconds': 238.860, 
         'cycles/seconds': 78.925 
    },

    # 'DECODE_S8': {
    #     'processing_time': {'value': 8991, 'unit': 'seconds'},
    #      'events/seconds': 203, 
    #      'cycles/seconds': 21 
    # },

    # 'FU_S15 + URS_S13': {
    #     'processing_time': {'value': 8935, 'unit': 'seconds'},
    #      'events/seconds': 213, 
    #      'cycles/seconds': 30 
    # },

    # 'ROB_S28': {
    #     'processing_time': {'value': 8490, 'unit': 'seconds'},
    #      'events/seconds': 221.691560, 
    #      'cycles/seconds': 29.633229 
    # },

    'ROB_S1': {
        'processing_time': {'value': 19513, 'unit': 'seconds'},
         'events/seconds': 139.532472, 
         'cycles/seconds': 55.940867 
    },

    'MEMORY': {
        'processing_time': {'value': 9770, 'unit': 'seconds'},
         'events/seconds': 202, 
         'cycles/seconds': 36 
    },
}

# Create a color map
start = 0.0
stop = 1.0
number_of_lines= len(timing_data)
cm_subsection = np.linspace(start, stop, number_of_lines) 
colors = [matplotlib.cm.viridis(x) for x in cm_subsection]

#hist
names = timing_data.keys()
processing_times = [timing_data[k]['processing_time']['value'] for k in names]
events_per_second = [timing_data[k]['events/seconds'] for k in names]
cycles_per_second = [timing_data[k]['cycles/seconds'] for k in names]

if args.plot:
    num_plots = 3

    # Create subplots based on the number of buffer_data items
    num_cols = 3
    num_rows = (num_plots // num_cols) + 1 if num_plots % num_cols != 0 else (num_plots // num_cols)

    fig, axs = plt.subplots(num_rows, num_cols, figsize=(num_cols*3, num_rows*2), dpi=400)
    
    # Add gaps between subplots
    plt.subplots_adjust(wspace=0.2, hspace=0.2)
      
    for i, name, data in [(0,'Duração (segundos)', processing_times), (1,'Eventos/segundo', events_per_second), (2, 'Ciclos/segundo', cycles_per_second)]:
        ax = axs[i % num_cols]    
        # ax = axs[(i // num_cols) % num_rows, i % num_cols]       
           
        ax.grid(axis='y', linestyle='--', color='black')
        
        ax.set_title(
            name,
            fontsize=11,
            # y=0.92, va="top", 
            # bbox=dict(facecolor='none', edgecolor='k')
        )

        # Set the fontsize for the ticks' text
        ax.tick_params(axis='both', which='major', labelsize=11)
        ax.tick_params(axis='both', which='minor', labelsize=11)

        ax.set_xticks(range(len(names)))
        ax.set_xticklabels([])

        # Plot histogram on each subplot with different colors and labels
        for idx, data_value in enumerate(data):
            ax.bar(idx, data_value, width=1.0, align="center", ec="k", color=colors[idx])

    c = 0
    for i in range(0, num_rows):
        for j in range(0, num_cols):
            c = c + 1
            if c > num_plots:
                axs[i, j].axis('off')

    #create legend
    handles = [matplotlib.patches.Rectangle((0,0),1,1,color=c,ec="k") for c in colors]
    plt.legend(handles, names, bbox_to_anchor=(1.2, 0.5), loc='center left')

    # plt.yticks(list(plt.yticks()[0]) + [buffer_positions[-1]])
    # plt.subplots_adjust(bottom=0.8)  # Adjust as needed
    plt.tight_layout()
    
    plt.savefig("phases_plot.png" if args.name == None else "%s.png" % args.name)

    if args.show:
        plt.show()
