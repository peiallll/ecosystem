import matplotlib.pyplot as plt

plt.ion()  # interactive mode ON

fig, ax = plt.subplots()
# three lines: prey, bushes, predators
line_prey, = ax.plot([], [], color="blue", label="Prey")
line_bush, = ax.plot([], [], color="green", label="Bushes")
line_pred, = ax.plot([], [], color="red", label="Predators")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Population")
ax.set_title("Population / Time")
ax.legend()

def update_plot(times, prey_pops, bush_pops, pred_pops):
    # update each line's data and rescale axes
    line_prey.set_xdata(times)
    line_prey.set_ydata(prey_pops)
    line_bush.set_xdata(times)
    line_bush.set_ydata(bush_pops)
    line_pred.set_xdata(times)
    line_pred.set_ydata(pred_pops)
    ax.relim()
    ax.autoscale_view()
    plt.pause(0.001)