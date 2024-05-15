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

buffer_data = {}
final_cycle = int(0)

# le e trata o arquivo de informações dos acessos passado para a opção -i
with open(args.info, 'r') as info:
    #aux
    buffer_positions = []
    buffer_positions_percents = []

    # lê primeira linha
    line = info.readline()

    while line:
        line_split = line[:-1].split(":")
        buffer_name = line_split[0]

        # processa linha
        if buffer_name != "cycle":
            buffer_data_array_or_final_cycle = eval(line_split[1])
            buffer_positions = list(range(len(buffer_data_array_or_final_cycle)))
            buffer_positions_percents = [float(position_count/final_cycle) for position_count in buffer_data_array_or_final_cycle]

            buffer_data.update({ buffer_name: {
                "counts": buffer_data_array_or_final_cycle,
                "positions": buffer_positions,
                "weights": buffer_positions_percents
            }})

        else:
            final_cycle = int(line_split[1])

        # le próxima linha
        line = info.readline()

if args.plot:
    # Get the number of buffer_data items
    num_plots = len(buffer_data)

    # Create subplots based on the number of buffer_data items
    num_cols = 3
    num_rows = (num_plots // num_cols) + 1 if num_plots % num_cols != 0 else 0

    fig, axs = plt.subplots(num_rows, num_cols, figsize=(num_cols*3, num_rows*2.5), dpi=100)
    
    # Add gaps between subplots
    plt.subplots_adjust(wspace=0.2, hspace=0.2)

    # Iterate over buffer_data items and plot histograms
    ymax = 0.0
    for i, (buffer_name, data) in enumerate(buffer_data.items()):
        buffer_counts = data.get("counts")
        for count in buffer_counts:
            if count/final_cycle > ymax:
                ymax = count/final_cycle

    for i, (buffer_name, data) in enumerate(buffer_data.items()):
        buffer_positions = data.get("positions")
        buffer_counts = data.get("counts")
        buffer_weigths = [count/final_cycle for count in buffer_counts]
        
        ax = axs[(i // num_cols) % num_rows, i % num_cols]       
        ax.grid(axis='y', linestyle='--', color='black')
        
        ax.set_title(buffer_name)

        # ymax = final_cycle
        # ymax = 1.0
        # ymax = 0.5
        ax.set_ylim([0.0, ymax])

        if args.log:
            # seta os ticks do eixo y
            l = np.log10(final_cycle)
            ticks = [0, int(final_cycle/(1024*l)), int(final_cycle/(32*l)), int(final_cycle/(2*l)), int(final_cycle/(l/2)), final_cycle]
            ax.set_yscale("symlog")
            ax.get_yaxis().set_major_formatter(ticker.ScalarFormatter(useOffset=False))
            # Calculate positions for subticks halfway between major ticks
            subticks = [int(ticks[i-1]+((ticks[i]-ticks[i-1])/2)) for i in range(1, len(ticks))]
            # Set the minor ticks at the calculated positions
            ax.yaxis.set_minor_locator(ticker.FixedLocator(subticks))
            ax.set_yticks(ticks)

        else:
            # seta os ticks do eixo y
            # last = ymax
            # step = int((ymax + 2)/4)
            # ticks = list(range(0, ymax + 1, step if step != 0 else 1))
            # if not last in ticks:
            #     if (last - ticks[-1]) <= int(step/2):
            #         ticks.pop(-1)
            #     ticks.append(last)
            # ax.set_yticks(ticks)
            # # ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
            ticks = [ymax*n for n in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]]
            ax.set_yticks(ticks)
            ax.get_yaxis().set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
        
        if i % num_cols != 0:
            ax.set_yticklabels([])
        
        # seta os ticks do eixo x
        # ax.set_xlim(-0.5, len(buffer_positions)-0.5)
        ax.set_aspect('auto')

        last = len(buffer_positions)-1
        step = int((len(buffer_positions)+1)/4)
        ticks = list(range(0, len(buffer_positions), step if step != 0 else 1))
        if not last in ticks:
            if (last - ticks[-1]) <= int(step/2):
                ticks.pop(-1)
            ticks.append(len(buffer_positions)-1)
        ax.set_xticks(ticks)

        # Plot histogram on each subplot
        # ax.bar(buffer_positions, buffer_counts, width=1.0, align="center")
        ax.bar(buffer_positions, buffer_weigths, width=1.0, align="center")

    c = 0
    for i in range(0, num_rows):
        for j in range(0, num_cols):
            c = c + 1
            if c > num_plots:
                axs[i, j].axis('off')

    plt.yticks(list(plt.yticks()[0]) + [buffer_positions[-1]])
    plt.tight_layout()
    
    plt.savefig("plot.png" if args.name == None else "%s.png" % args.name)

    if args.show:
        plt.show()
