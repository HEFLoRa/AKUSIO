import numpy as np
from fusion.fusion_center import FusionCenter
from fusion.model import Bearing

"""
Example Scenario:
    - 2 targets A & B
    - A: detected every 50 seconds
    - B: detected every 60 seconds


"""


def simulate():
    # Scenario parameters
    FC = FusionCenter()
    def_model(FC)
    hypothesis = []
    target_A = Target(np.array([2.0, 2.0]), np.array([0.0, -1.0]), 0)
    target_B = Target(np.array([-2.0, -2.0]), np.array([0.0, 1.0]), 1)
    targets = [target_A, target_B]
    timestamp = 0

    delay_between_target_A_meas = 50
    delay_between_target_B_meas = 60

    n_targets_per_time = []

    n_trials = 1000
    for i in range(0, n_trials):

        hypothesis = FC.prediction(timestamp, hypothesis)
        bearing = None
        if timestamp % delay_between_target_A_meas == 0:
            bearing = produce_rnd_measurement(FC, targets, target_A)
            print("Target A (0) bearing")
        elif timestamp % delay_between_target_B_meas == 0:
            bearing = produce_rnd_measurement(FC, targets, target_B)
            print("Target B (1) bearing")
        if bearing is not None:

            hypothesis, n_targets, n_targets_per_class = FC.update(timestamp, hypothesis, bearing, simulate_classification(FC, targets))
            print("Estimated number of targets: " + str(FC.n_targets))
            print(n_targets_per_class)

        n_targets = np.sum([np.round(n) for n in n_targets_per_class])
        n_targets_per_time.append(n_targets)
        move_target(targets)
        timestamp += 1.0


def simulate_classification(FC, targets):
    prob_classification = 0.7
    prob_classification = 0.1

    counter_classes = np.zeros(FC.model.n_bird_classes)
    classification = np.zeros(FC.model.n_bird_classes)

    for target in targets:
        counter_classes[target.classification] += 1

    for i, counter in enumerate(counter_classes):
        if counter > 0:
            classification[i] = prob_classification
            classification[i] = np.clip(prob_classification + 0.1 * counter, 0, 1.0)
        else:
            classification[i] = 0.005 # np.random.uniform(0.1, 0.1)

    return classification


def produce_rnd_measurement(FC, targets, goal_target=None, sensor=None):
    if sensor is None:
        sensor_pos = FC.model.sensors[0].position
    else:
        sensor_pos = sensor.position

    if not targets and goal_target is None:
        return Bearing(sensor_pos, np.random.uniform(-np.pi, np.pi), FC.model.R)

    if goal_target is not None:
        target = goal_target.position
    else:
        target = np.random.choice(targets).position

    r = np.sqrt((sensor_pos[0] - target[0]) ** 2 + (sensor_pos[1] - target[1]) ** 2)
    theta = np.arctan2((target[1] - sensor_pos[1]), target[0] - sensor_pos[0])

    #if theta < 0:
        #theta = 2.0 * np.pi + theta

    # theta_noisy = theta + np.random.normal(theta, FC.model.R)
    theta = theta + np.random.normal(0, FC.model.R)

    return Bearing(sensor_pos, theta, FC.model.R)

class Target:
    def __init__(self, position, direction, classification):
        self.position = position
        self.direction = direction
        self.classification = classification

def def_model(FC):
    """
    kappa is currently to small
    :param FC:
    :return:
    """
    FC.model.merge_threshold = 1.0
    FC.model.prune_threshold = 0.00001
    FC.model.association_threshold = 0.15
    FC.model.kappa = 0.01  # 0.02
    FC.model.p_S = 0.999
    FC.model.measurement_hypo_w = 0.9


def move_target(targets):
    stepsize = 0.005
    for target in targets:
        target.position = target.position + np.power(-1, np.random.randint(1, 3)) * target.direction * stepsize


if __name__ == '__main__':
    simulate()
