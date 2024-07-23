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

with_hist_timing_data = {
    'Modo Contínuo': {
        # '10': {
        #     'processing_time': {'value': 0.038, 'unit': 'seconds'},
        #     'events/second': 265.887, 
        #     'cycles/second': 0.000
        # },
        '100': {
            'processing_time': {'value': 7.136, 'unit': 'seconds'},
            'events/second': 14.013,
            'cycles/second': 6.166
        },
        '1000': {
            'processing_time': {'value': 49.242, 'unit': 'seconds'},
            'events/second': 20.308,
            'cycles/second': 6.458
        },
        '10000': {
            'processing_time': {'value': 263.781, 'unit': 'seconds'},
            'events/second': 37.910,
            'cycles/second': 5.838
        },
        '100000': {
            'processing_time': {'value': 1819.293, 'unit': 'seconds'},
            'events/second': 54.966,
            'cycles/second': 5.518
        }
    },
    'Modo Salto': {
        # '10': {
        #     'processing_time': {'value': 0.001, 'unit': 'seconds'},
        #     'events/second': 7447.059, 
        #     'cycles/second': 0.000
        # },
        '100': {
            'processing_time': {'value': 6.221, 'unit': 'seconds'},
            'events/second': 16.075,
            'cycles/second': 7.073
        },
        '1000': {
            'processing_time': {'value': 41.731, 'unit': 'seconds'},
            'events/second': 23.963,
            'cycles/second': 7.620
        },
        '10000': {
            'processing_time': {'value': 210.861, 'unit': 'seconds'},
            'events/second': 47.425,
            'cycles/second': 7.303
        },
        '100000': {
            'processing_time': {'value': 1427.405, 'unit': 'seconds'},
            'events/second': 70.057,
            'cycles/second': 7.032
        }
    },
    'Modo Salto Rápido': {
        # '10': {
        #     'processing_time': {'value': 0.002, 'unit': 'seconds'},
        #     'events/second': 6274.211,
        #     'cycles/second': 0.000
        # },
        '100': {
            'processing_time': {'value': 0.022, 'unit': 'seconds'},
            'events/second': 4459.288,
            'cycles/second': 1962.087
        },
        '1000': {
            'processing_time': {'value': 0.032, 'unit': 'seconds'},
            'events/second': 31127.120,
            'cycles/second': 9898.424
        },
        '10000': {
            'processing_time': {'value': 0.204, 'unit': 'seconds'},
            'events/second': 48981.025,
            'cycles/second': 7543.078
        },
        '100000': {
            'processing_time': {'value': 1.671, 'unit': 'seconds'},
            'events/second': 59837.030,
            'cycles/second': 6006.441
        }
    }
}



no_hist_timing_data = {
    'Modo Contínuo': {
        # '10': {
        #     'processing_time': {'value': 0.045, 'unit': 'seconds'},
        #     'events/second': 219.801, 
        #     'cycles/second': 0.000
        # },
        '100': {
            'processing_time': {'value': 0.459, 'unit': 'seconds'},
            'events/second': 217.738,
            'cycles/second': 95.805
        },
        '1000': {
            'processing_time': {'value': 4.500, 'unit': 'seconds'},
            'events/second': 222.225,
            'cycles/second': 70.668
        },
        '10000': {
            'processing_time': {'value': 46.073, 'unit': 'seconds'},
            'events/second': 217.049,
            'cycles/second': 33.426
        },
        '100000': {
            'processing_time': {'value': 435.552, 'unit': 'seconds'},
            'events/second': 229.594,
            'cycles/second': 23.047
        }
    },
    'Modo Salto': {
        # '10': {
        #     'processing_time': {'value': 0.001, 'unit': 'seconds'},
        #     'events/second': 12213.949, 
        #     'cycles/second': 0.000
        # },
        '100': {
            'processing_time': {'value': 0.113, 'unit': 'seconds'},
            'events/second': 882.674,
            'cycles/second': 388.377
        },
        '1000': {
            'processing_time': {'value': 0.704, 'unit': 'seconds'},
            'events/second': 1420.337,
            'cycles/second': 451.667
        },
        '10000': {
            'processing_time': {'value': 8.694, 'unit': 'seconds'},
            'events/second': 1150.237,
            'cycles/second': 177.136
        },
        '100000': {
            'processing_time': {'value': 91.056, 'unit': 'seconds'},
            'events/second': 1098.230,
            'cycles/second': 110.240
        }
    },
    'Modo Salto Rápido': {
        # '10': {
        #     'processing_time': {'value': 0.001, 'unit': 'seconds'},
        #     'events/second': 7168.865,
        #     'cycles/second': 0.000
        # },
        '100': {
            'processing_time': {'value': 0.048, 'unit': 'seconds'},
            'events/second': 2091.942,
            'cycles/second': 920.454
        },
        '1000': {
            'processing_time': {'value': 0.061, 'unit': 'seconds'},
            'events/second': 16438.915,
            'cycles/second': 5227.575
        },
        '10000': {
            'processing_time': {'value': 0.182, 'unit': 'seconds'},
            'events/second': 54935.589,
            'cycles/second': 8460.081
        },
        '100000': {
            'processing_time': {'value': 1.378, 'unit': 'seconds'},
            'events/second': 72589.259,
            'cycles/second': 7286.510
        }
    }
}

# timing_data = no_hist_timing_data
timing_data = with_hist_timing_data

# Create a color map
start = 0.0
stop = 0.7
number_of_lines= 3
colors = [matplotlib.cm.plasma(0.0), matplotlib.cm.plasma(0.5), matplotlib.cm.plasma(0.7)]

#hist
# names = timing_data.keys()
names = {
    'Modo Contínuo',
    'Modo Salto',
    'Modo Salto Rápido'
}

processing_times = {}
for k in names:
    processing_times[k] = [timing_data[k][l]['processing_time']['value'] for l in timing_data[k].keys()]
# print("processing_times: ", processing_times)

events_per_second = {}
for k in names:
    events_per_second[k] = [timing_data[k][l]['events/second'] for l in timing_data[k].keys()]
# print("\nevents_per_second: ", events_per_second)

# cycles_per_second = {}
# for k in names:
#     cycles_per_second[k] = [timing_data[k][l]['cycles/second'] for l in timing_data[k].keys()]
# print("\ncycles_per_second: ", cycles_per_second)

if args.plot:
    num_plots = 1

    # Create subplots based on the number of buffer_data items
    num_cols = 2
    num_rows = (num_plots // num_cols) + 1 if num_plots % num_cols != 0 else (num_plots // num_cols)

    fig, axs = plt.subplots(num_rows, num_cols, figsize=(num_cols*4, num_rows*2), dpi=300)
    
    # Add gaps between subplots
    plt.subplots_adjust(wspace=0.2, hspace=0.2)
      
    for i, name, data in [
        (0,'Duração (segundos)', processing_times),
        (1,'Eventos/segundo', events_per_second),
        # (2, 'Ciclos/segundo', cycles_per_second)
    ]:

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

        ax.set_xticks([100, 1000, 10000, 100000])
        ax.set_xticklabels([])

        if args.log:
            ax.set_xscale('log')
            ax.set_xticks([100, 1000, 10000, 100000])
            ax.set_yscale('log')

        # Plot histogram on each subplot with different colors and labels
        for idx, values in enumerate(data.values()):
            ax.plot([100, 1000, 10000, 100000], values, color=colors[idx])
            # ax.plot([100, 1000, 10000, 100000], values, color=colors[2])
        # ax.legend()

        # ax.set_ylim([0.0, 2000.0])

        # for idx, data_value in enumerate(data):
        #     ax.bar(idx, data_value, width=1.0, align="center", ec="k", color=colors[idx])

    # c = 0
    # for i in range(0, num_rows):
    #     for j in range(0, num_cols):
    #         c = c + 1
    #         if c > num_plots:
    #             axs[i, j].axis('off')

    #create legend
    handles = [matplotlib.patches.Rectangle((0,0),1,1,color=c,ec="k") for c in colors]
    # handles = [matplotlib.patches.Rectangle((0,0),1,1,color=c,ec="k") for c in colors[2:]]
    plt.legend(handles, names, bbox_to_anchor=(1.2, 0.5), loc='center left')

    # plt.yticks(list(plt.yticks()[0]) + [buffer_positions[-1]])
    # plt.subplots_adjust(bottom=0.8)  # Adjust as needed
    plt.tight_layout()
    
    plt.savefig("phases_plot.png" if args.name == None else "%s.png" % args.name)

    if args.show:
        plt.show()
