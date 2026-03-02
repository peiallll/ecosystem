import matplotlib.pyplot as plt

plt.ion()  # interactive mode ON

fig, ax = plt.subplots()
line, = ax.plot([], [], color="blue")
ax.set_xlabel("Time (s)")
ax.set_ylabel("popultion")
ax.set_title("population/time")

def update_plot(times, populations):
    line.set_xdata(times)
    line.set_ydata(populations)
    ax.relim()
    ax.autoscale_view()
    plt.pause(0.001)