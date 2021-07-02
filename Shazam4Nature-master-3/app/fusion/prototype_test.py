import fusion.visualization as vis
import numpy as np
from matplotlib import patches
from fusion.model_2 import Bearing
from fusion.fusion_center_2 import FusionCenter
from fusion.simulator import Target
import fusion.simulator as simulator

"""
Test Scenario for the prototype FusionCenter:
"""


def simulate():
    # Scenario parameters
    FC = FusionCenter()
    def_model(FC)
    hypothesis = []
    target_A = Target(np.array([2.0, 2.0]), np.array([0.0, -1.0]), 0)
    target_B = Target(np.array([2.0, 0.0]), np.array([0.0, 1.0]), 1)
    target_C = Target(np.array([2.0, -2.0]), np.array([0.0, -1.0]), 2)
    target_D = Target(np.array([0.0, -2.0]), np.array([0.0, 1.0]), 3)
    target_E = Target(np.array([-2.0, -2.0]), np.array([0.0, 1.0]), 4)
    target_F = Target(np.array([-2.0, 0.0]), np.array([0.0, 1.0]), 5)
    target_G = Target(np.array([-2.0, 2.0]), np.array([0.0, 1.0]), 6)
    target_H = Target(np.array([0.0, 2.0]), np.array([0.0, 1.0]), 7)

    pos_targets = [target_A, target_B, target_C, target_D, target_E, target_F, target_G, target_H]

    targets = []
    timestamp = 0

    sensor = FC.model.sensors[0]

    N = 100
    delay_between_bearings = 10
    # Visualization parameters
    init_vis(FC)
    bounding_circle = patches.Circle((sensor.position[0], sensor.position[1]), radius=FC.model.max_range,
                                     edgecolor='black', fill=False, linestyle="dotted")

    n_targets_per_time = []
    n_GT_targets_per_time = []
    trials = 1000

    for i in range(trials):
        vis.reset()
        vis.ax.add_patch(bounding_circle)
        simulator.plt_targets(targets, color='navy')

        hypothesis = FC.prediction(timestamp, hypothesis)
        bearing = None
        if timestamp % N == 0:
            n = np.random.randint(1, 5)
            targets = np.random.choice(pos_targets, n)
            print("New targets: ")
            for target in targets:
                print(str(target.classification))

        if timestamp % delay_between_bearings == 0:
            if len(targets) == 0:
                bearing = simulator.produce_rnd_measurement(FC, [])
            else:
                target = np.random.choice(targets)
                print("Target class "+str(target.classification))
                bearing = simulator.produce_rnd_measurement(FC, targets, target)

        if bearing is not None:
            simulator.plt_hypothesis(hypothesis, color='blue')
            #vis.plot_pause(1.0)

            simulator.plt_bearing(bearing, FC.model.max_range)
            hypothesis, n_targets, n_targets_per_class = FC.update(timestamp, hypothesis, bearing,
                                                                   simulator.simulate_classification(FC, targets))
            simulator.plt_hypothesis(hypothesis, color='red')
            n_target_round = np.round(n_targets_per_class)
            print(n_targets_per_class)
            print("Estimated number of targets: " + str(np.sum(n_targets_per_class)) + "("+str(len(targets))+")")
            #vis.plot_pause(2.0)

        n_targets_per_time.append(np.sum(n_target_round))
        n_GT_targets_per_time.append(len(targets))

        move_target(targets)
        timestamp += 1.0
        vis.update()

    vis.reset()
    vis.ax.plot(np.arange(trials), n_targets_per_time, label='Estimated Number')
    vis.ax.plot(np.arange(trials), n_GT_targets_per_time, label="GT")
    vis.fig.show()

def def_model(FC):
    """
    :param FC:
    :return:
    """
    FC.model.merge_T = 1.0
    FC.model.prune_T = 0.0001
    FC.model.association_T = 0.20#0.17
    FC.model.kappa = 0.04#0.015
    FC.model.p_S = 0.995
    FC.model.measurement_hypo_w = 0.7


def init_vis(FC):
    xmax = FC.model.x_range
    xmin = -FC.model.x_range
    ymax = FC.model.y_range
    ymin = -FC.model.y_range
    vis.init_vis(xmin, xmax, ymin, ymax)
    vis.register_elements({"Prediction": 'blue',
                           "Filtering": 'red',
                           "Measurement": 'yellow',
                           "Target": 'navy'})


def move_target(targets):
    stepsize = 0.005
    for target in targets:
        target.position = target.position + np.power(-1, np.random.randint(1, 3)) * target.direction * stepsize


if __name__ == '__main__':
    simulate()
