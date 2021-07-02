import fusion.visualization as vis
import numpy as np
from fusion.fusion_center import FusionCenter
from matplotlib import patches
import tkinter


def simulate_phd_filter(FC):
    xmax = FC.model.x_range
    xmin = -FC.model.x_range
    ymax = FC.model.y_range
    ymin = -FC.model.y_range
    vis.init_vis(xmin, xmax, ymin, ymax)

    timestamp = 0
    sensor = FC.model.sensors[0]
    hypothesis = []

    vis.register_elements({"Hypothesis after Birth":'green', "Prediction":'blue', "Filtering":'red', "Measurement":'yellow'})
    while True:
        vis.reset()
        vis.plot_sensor(sensor)
        max_range_bound = patches.Circle((sensor.position[0], sensor.position[1]), radius=FC.model.max_range,
                                         edgecolor='black', fill=False, linestyle="dotted")
        vis.ax.add_patch(max_range_bound)

        hypothesis = FC.produce_random_birth_targets(timestamp, hypothesis)
        plt_hypothesis(hypothesis, color='green')
        vis.plot_pause(1.5)

        hypothesis = FC.prediction(timestamp, hypothesis)
        plt_hypothesis(hypothesis, color='blue')
        vis.plot_pause(1.5)

        if timestamp % 2 == 0:
            bearing = produce_rnd_measurement()
            measurements = FC.bearing_to_measurements(bearing)
            plt_measurements(measurements)
            vis.plot_pause(1.5)

            hypothesis, n_targets = FC.update(timestamp, hypothesis, bearing, [])
            print("Estimated number of targets: "+str(n_targets))
            plt_hypothesis(hypothesis, color='red')
            vis.plot_pause(1.5)

        timestamp += 1.0
        vis.update()


def produce_rnd_measurement():
    return np.random.uniform(0.0, 2*np.pi)


def plt_hypothesis(hypothesis, color='black'):
    for hypo in hypothesis:
        vis.plot_state(hypo.x, color=color, label=str(round(hypo.w, 3)))
        cov = get_ellipse_2D(hypo.x, hypo.P)
        vis.plot_ellipse(cov, color=color)


def plt_measurements(measurements):
    for meas in measurements:
        vis.plot_state(meas.x, color='yellow')
        cov = get_ellipse_2D(meas.x, meas.R)
        vis.plot_ellipse(cov, color='yellow')


def get_ellipse_2D(position, R):

    B = np.linalg.cholesky(R[0:2, 0:2])
    steps = 1000
    stepsize = 2*np.pi/steps
    t = 0
    z = np.zeros(2)
    ellipse = np.zeros((2,steps))

    for step in range(0, steps):
        z[0] = 2.0 * np.cos(t)
        z[1] = 2.0 * np.sin(t)
        ellipse[:, step] = np.dot(B, z) + position[0:2]
        t += stepsize

    return ellipse


if __name__ == '__main__':
    FC = FusionCenter()
    simulate_phd_filter(FC)
