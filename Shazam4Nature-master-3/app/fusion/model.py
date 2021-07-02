import numpy as np
import copy


class Model:
    def __init__(self):

        # number of different bird classes
        self.n_bird_classes = 19
        # bounding rectangle for new generated targets
        self.x_range = 3
        self.y_range = 3

        # list of sensors
        self.sensors = [Sensor("1", np.zeros(2))]

        """ sensor model - fixed for all sensors """
        # measurement matrix
        self.H = np.eye(2, 2)
        # bearing variance in radiance
        self.R = np.deg2rad(15)
        # max sensor range in meters
        self.max_range = 3.0

        # detection probability - will be adapted w.r.t. classification
        self.p_D = 0.95
        # number of measurements per bearing
        self.N = 6

        """ dynamics - multiple dynamic model according to bird class"""
        # survival probability
        self.p_S = 0.999
        # dictionary of dynamic models
        self.dynamics = {0: DynamicalModel(0, np.array([[1, 0], [0, 1]]),
                                           np.eye(2, 2) * 0.1)}

        """ PHD-Filter parameters """
        # target birth parameters
        self.birth_w = 0.1
        self.birth_cov = np.eye(2, 2) * 1.2**2
        # if we sample more new hypothesis our overall estimated number will increase
        self.max_n_births = 1
        
        # update/filtering parameters
        self.prune_threshold = 0.00001
        self.merge_threshold = 1.0
        self.contribution_threshold = 0.02
        """
        #false_alarms / |FoV|
        kappa has a huge impact on the weights of new hypothesis in the update step if we can associate the bearing
           - large kappa
                   - expect a large number of false alarms
                   - if association: small weights 
           - small kappa
                   - expect a small number of false alarms
                   - if association: large weights
        """
        self.kappa = 0.02

        """
        I would say a proper association threshold depends on the expected number of targets in the area:
            - lets say we will have a large number of targets -> we need a large threshold to associate the bearing
            - if we have a small number -> the threshold should be small o/w we would always assume a new target
        """
        self.association_threshold = 0.25

        # prob. of p(hypo_class | correct_class)
        self.classification_prob = 0.9
        # initial. weight of new GM produced in the update step
        self.measurement_hypo_w = 0.9

        
class DynamicalModel:
    def __init__(self, id, F, Q):
        self.id = id
        self.F = F
        self.Q = Q


class Sensor:
    def __init__(self, id, position):
        """
        :param id: id of the sensor (pi)
        :param position: UTM position of the sensor
        """
        self.id = id
        self.position = position


class Bearing:
    def __init__(self, position, angle, sigma):
        self.position = position
        self.angle = angle
        self.sigma = sigma


class Hypothesis:

    def __init__(self, timestamp, w, x, P, classification=None):
        """
        
        :param timestamp: UTC timestamp 
        :param w: weight
        :param x: state 
        :param P: covariance matrix
        :param classification: list of doubles, each correspond to a prob. for a certain bird
        @note: classification could also be a dictionary: key = bird type, value = prob. of that bird
        """
        self.timestamp = timestamp
        self.w = w
        self.x = x
        self.P = P
        self.classification = copy.deepcopy(classification)

    def __str__(self):
        return str(self.timestamp) + " - " + str(self.w) + " - " + str(self.x) + " - " + str(self.P)


class Measurement:
    def __init__(self, x, R):
        self.x = x
        self.R = R
