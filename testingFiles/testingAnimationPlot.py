import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import numpy as np
import psutil
from collections import deque


def frames_plot(i):
    """
    Live shows x and y data. x and y must be the same lenght

    Parameters
    ----------

    """
    global cpu
    global ax

    cpu.pop(0)
    cpu.append(psutil.cpu_percent())

    ax.cla()

    ax.plot(cpu)
    ax.scatter(len(cpu)-1, cpu[-1])
    ax.text(len(cpu)-1, cpu[-1]+2, "{}%".format(cpu[-1]))


cpu = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
ax = plt.subplot(111)
ax.set_facecolor('#DEDEDE')
fig = plt.figure(figsize=(12, 6))

ani = anim.FuncAnimation(fig, frames_plot, interval=500)

plt.show()

