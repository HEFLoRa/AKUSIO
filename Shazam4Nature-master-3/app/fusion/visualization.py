import os

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

"""
Helper functions to handle the visualization of the simulation
"""

fig = plt.figure("Track")
ax = fig.add_subplot(111)

legend_patches = []

xlim = []
ylim = []


def init_vis(x_min, x_max, y_min, y_max):
    global xlim, ylim
    xlim = [x_min, x_max]
    ylim = [y_min, y_max]

    ax.spines['left'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_position('zero')
    ax.spines['top'].set_color('none')
    ax.spines['left'].set_smart_bounds(True)
    ax.spines['bottom'].set_smart_bounds(True)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.axhline(linewidth=2, color='black')
    ax.axvline(linewidth=2, color='black')
    ax.set_xlabel('x')
    ax.set_ylabel('y')

    ax.axis('equal')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    ax.legend(handles=legend_patches)

    plt.ion()

    fig.show()
    fig.canvas.draw()


def register_elements(elements):
    global legend_patches
    patches = []
    for id in elements:
        patches.append(mpatches.Patch(color=elements[id], label=id))

    legend_patches = patches


def reset():
    global xlim, ylim
    ax.clear()
    # ax_cov.clear()
    # redefine ax
    ax.spines['left'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_position('zero')
    ax.spines['top'].set_color('none')
    ax.spines['left'].set_smart_bounds(True)
    ax.spines['bottom'].set_smart_bounds(True)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.axhline(linewidth=2, color='black')
    ax.axvline(linewidth=2, color='black')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.axis('equal')

    ax.legend(handles=legend_patches)


def update():
    try:
        fig.canvas.draw()
    except Exception:
        plt.ioff()
        plt.close('all')
        os._exit(0)


def end():
    try:
        plt.ioff()
        # plt.show()
        plt.close('all')
        os._exit(0)
    except Exception:
        pass


def plot_sensor(sensor, color='red'):
    ax.plot(sensor.position[0], sensor.position[1], color=color, marker='^')


def plot_ellipse(ellipse, color='black'):
    ax.plot(ellipse[0, :], ellipse[1, :], color=color)


def plot_ellipse_patch(ellipse):
    ax.add_patch(ellipse)


def plot_state(state, color='blue', label=None):
    if label is not None:
        ax.plot(state[0], state[1], color=color, marker='x')
        ax.text(state[0], state[1], label, fontsize=9)
    else:
        ax.plot(state[0], state[1], color=color, marker='x')


def plot_track(track_pos, s_ind=0, e_ind=None, color='black'):
    if e_ind is None:
        e_ind = track_pos.shape[1]
    ax.plot(track_pos[0, s_ind:e_ind], track_pos[1, s_ind:e_ind], color=color)


def plot_pause(time):
    plt.pause(time)
