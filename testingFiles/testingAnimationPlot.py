import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import numpy as np
import psutil
from collections import deque


def main():
    cpu = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    fig = plt.figure()

    ax = plt.subplot(111)
    ax.set_facecolor('#DEDEDE')

    def frames_plot(i):
        """
        Live shows x and y data. x and y must be the same lenght

        Parameters
        ----------

        """
        cpu.pop(0)
        cpu.append(psutil.cpu_percent())

        ax.cla()

        ax.plot(cpu)
        ax.text(len(cpu) - 1, cpu[-1] + 2, "{}%".format(cpu[-1]))
        ax.set_ylim([0, 100])

    ani = anim.FuncAnimation(fig, frames_plot, interval=1000)

    plt.show()

main()