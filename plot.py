import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def draw_gaant_pcmax(schedule, filename:str, makespan=None):

    fig, ax = plt.subplots(figsize=(10,5))
    colors = plt.cm.tab20.colors

    num_machines = len(schedule)
    machines = list(schedule.keys())

    for machine_index, (machine, tasks) in enumerate(schedule.items()):
        for task_id, start, duration in tasks:
            color = colors[task_id % len(colors)]
            ax.barh(
                y=machine_index,
                width=duration,
                left=start, 
                height=0.6,
                align='center',
                color=color,
                edgecolor='black',
                alpha=0.85
            )
            ax.text(
                start + duration / 2,
                machine_index,
                f"J{task_id}\n{duration}",
                ha='center',
                va='center',
                color='black',
                fontsize=9,
                weight='bold'
            )
    if makespan is not None:
        ax.axvline(x=makespan, color='red', linestyle='--', linewidth=2, label=f'$C_{{max}} = {makespan}$')
        ax.legend(loc='upper right')

    ax.set_yticks(range(num_machines))
    ax.set_yticklabels(machines)
    ax.invert_yaxis()
    ax.set_xlabel("Time")
    ax.set_ylabel("Machines")
    ax.set_title("Gaant Diagram - PCMAX")
    ax.grid(axis='x', linestyle=':', alpha=0.7)

    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close(fig)
    print(f"Gaant chart saved to: {filename}")