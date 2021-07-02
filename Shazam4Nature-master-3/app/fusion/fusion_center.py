from app.fusion.model import Model, Hypothesis, Measurement
import numpy as np
import copy
from numpy import sin, cos, transpose
from scipy.stats import multivariate_normal, norm
from scipy.linalg import inv
"""
Important Observation: if we receive a 'bad' bearing that can be associated only to small number
of prior hypothesis (or associated with a really small weight), we will loose a lot of hypotheses --> Therefore we loose a large sum of weights 
--> small estimated number of targets --> Can accumulate over time since the next bearing can also only be
associated to a small number of priors until we will initialize a new GM 

--> One Idea would be to define a min. number of association and if we don't reach the threshold we will
produce a new GM 
"""


class FusionCenter:

    def __init__(self):
        self.model = Model()
        self.current_time = 0.0
        self.n_targets = 0
        self.last_update_time = 0

    def produce_random_birth_targets(self, timestamp, hypothesis):
        """
        generates randomly new target hypothesis and add them to the current list
        :param timestamp: current time in UTC
        :param hypothesis: current set of hypothesis
        :return:
        """
        number_births = self.model.max_n_births
        # fixed initial covariance
        cov = np.copy(self.model.birth_cov)

        x_range = self.model.x_range
        y_range = self.model.y_range

        w_sum = 0.0
        for i in range(0, number_births):
            # random state
            rnd_state = np.array([np.random.uniform(-x_range, x_range), np.random.uniform(-y_range, y_range)])
            w = 1.0 / self.model.n_bird_classes
            # add new hypothesis
            for j in range(0, self.model.n_bird_classes):
                hypothesis.append(Hypothesis(timestamp, w, rnd_state, cov, j))
                w_sum += w

        self.n_targets = self.n_targets * self.model.p_S + w_sum
        return hypothesis

    # step 1
    def prediction(self, timestamp, hypothesis):
        """
        CHANGE: choose motion model w.r.t. to hypothesis classification

        :param timestamp: UTC timestamp
        :param hypothesis: set of current hypothesis
        :return: set of new predicted hypothesis
        """

        predicted = copy.deepcopy(hypothesis)

        p_S = self.model.p_S
        F = self.model.dynamics[0].F
        Q = self.model.dynamics[0].Q
        for hypo in predicted:
            #F = self.model.dynamics[hypo.classification].F
            #Q = self.model.dynamics[hypo.classification].Q
            hypo.timestamp = timestamp
            hypo.w = p_S * hypo.w
            hypo.x = F @ hypo.x
            hypo.P = Q + F @ hypo.P @ transpose(F)

        self.n_targets, n_targets_per_class = self.number_of_targets_per_class(predicted)
        return predicted

    def update2(self, timestamp, hypothesis, bearing, classification):
        """
        Second update function where we first associate every hypothesis with the bearing
        Then if the accumulated weight is larger than some threshold we will use this association
        If not reject (or not) and produce a new hypothesis set
        """
        non_normalized_classification = copy.deepcopy(classification)
        # normalize classification vector s.t. each entry is between 0 - 1
        classification = classification / np.sum(classification)

        J = len(hypothesis)
        updated = copy.deepcopy(hypothesis)

        # no detection hypotheses
        for j in range(J):
            p = self.adapt_detection_prob(timestamp)
            updated[j].w = (1.0 - p) * hypothesis[j].w

        bearing_contribution = 0.0
        contribution_threshold = self.model.contribution_threshold
        updated2 = []
        # threshold for association of the bearing and a hypothesis
        for c in range(self.model.n_bird_classes):
            n_new_hypothesis = 0
            sum_w = 0.0
            for hypo in hypothesis:
                # association value/weight
                w_association, H, S, hypo_angle = self.get_association_value(bearing, hypo)

                # model prob. depending on the classification
                w_classification = self.get_classification_prob(c, hypo)

                # weight computation: see notes
                w = self.adapt_detection_prob(timestamp) * w_classification * classification[
                    c] * hypo.w * w_association

                # Kalman Gain matrix
                K = hypo.P @ transpose(H) * 1.0 / S
                I = np.eye(hypo.P.shape[0])

                P = (I - K @ H) @ hypo.P @ (I - K @ H) + K * S @ transpose(K)

                x = hypo.x + K * (bearing.angle - hypo_angle)

                updated2.append(Hypothesis(timestamp, w, x, P, hypo.classification))
                n_new_hypothesis += 1
                sum_w += w
                bearing_contribution += w

            for j in range(n_new_hypothesis):
                updated2[-(j + 1)].w = updated2[-(j + 1)].w / (self.model.kappa + sum_w)

        if bearing_contribution < contribution_threshold:
            new_hypo = self.generate_measurement_hypothesis(timestamp, self.bearing_to_measurements(bearing),
                                                            non_normalized_classification)
            updated.extend(new_hypo)
        else:
            updated.extend(updated2)
            print("bearing associated")

        self.n_targets, n_targets_per_class = self.number_of_targets_per_class(hypothesis)
        hypothesis = self.pruning(updated)
        hypothesis = self.merge_hypothesis(hypothesis)
        self.n_targets, n_targets_per_class = self.number_of_targets_per_class(hypothesis)
        self.last_update_time = timestamp

        return hypothesis

    # step 2
    def update(self, timestamp, hypothesis, bearing, classification):

        non_normalized_classification = copy.deepcopy(classification)
        # normalize classification vector s.t. each entry is between 0 - 1
        classification = classification / np.sum(classification)

        J = len(hypothesis)
        updated = copy.deepcopy(hypothesis)

        # no detection hypotheses
        for j in range(J):
            p = self.adapt_detection_prob(timestamp)
            updated[j].w = (1.0 - p) * hypothesis[j].w

        bearing_associated = False
        # threshold for association of the bearing and a hypothesis
        for c in range(self.model.n_bird_classes):
            n_new_hypothesis = 0
            sum_w = 0.0
            for hypo in hypothesis:
                # association value/weight
                w_association, H, S, hypo_angle = self.get_association_value(bearing, hypo)
                if w_association > self.model.association_threshold:
                    bearing_associated = True
                    # model prob. depending on the classification
                    w_classification = self.get_classification_prob(c, hypo)

                    # weight computation: see notes
                    w = self.adapt_detection_prob(timestamp) * w_classification * classification[c] * hypo.w * w_association

                    # Kalman Gain matrix
                    K = hypo.P @ transpose(H) * 1.0/S
                    I = np.eye(hypo.P.shape[0])

                    # Simple Kalman update
                    # Note: We have to use the Joseph Form o/w for S ~ 1.0 the resulting covariance matrix P
                    # is not positive semi-definit
                    # Why: in the simple Kalman Update we have a subtraction that can result in loss of symmetry and
                    # positive definiteness due to rounding errors
                    # P = (I - K @ H) @ hypo.P
                    # Joseph Form update
                    # secures that the updated covariance is positive semi-definite at expense of computation burden
                    P = (I - K @ H) @ hypo.P @(I - K @ H) + K * S @ transpose(K)

                    x = hypo.x + K * (bearing.angle - hypo_angle)

                    updated.append(Hypothesis(timestamp, w, x, P, hypo.classification))
                    n_new_hypothesis += 1
                    sum_w += w

            for j in range(n_new_hypothesis):
                updated[-(j + 1)].w = updated[-(j + 1)].w / (self.model.kappa + sum_w)

        if not bearing_associated:
            new_hypo = self.generate_measurement_hypothesis(timestamp, self.bearing_to_measurements(bearing), non_normalized_classification)
            updated.extend(new_hypo)
        else:
            print("bearing associated")

        self.n_targets, n_targets_per_class = self.number_of_targets_per_class(hypothesis)
        hypothesis = self.pruning(updated)
        hypothesis = self.merge_hypothesis(hypothesis)
        self.n_targets, n_targets_per_class = self.number_of_targets_per_class(hypothesis)
        self.last_update_time = timestamp
        return hypothesis

    def get_classification_prob(self, c, hypo):
        if c == hypo.classification:
            return self.model.classification_prob
        else:
            return (1.0 - self.model.classification_prob)/(self.model.n_bird_classes - 1)

    def get_association_value(self, bearing, hypo):
        """
        If S is closely to 1.0 the resulting covariance P will be positive semidefinite:
                [~0, -x]
                [-y, ~0]
                with x, y >> 0.0
        """
        x = hypo.x[0]
        y = hypo.x[1]

        sensor_pos = self.model.sensors[0].position
        hypo_z = np.arctan2((y - sensor_pos[1]), x - sensor_pos[0])

        # gradient of arctan2
        H = np.array([-y/(x**2 + y**2), x/(x**2 + y**2)])

        # corresponding innovation covariance
        S = H @ hypo.P @ transpose(H) + bearing.sigma

        N = norm(loc=hypo_z, scale=S)
        # association value/weight
        w_association = N.pdf(bearing.angle)

        return w_association, H, S, hypo_z

    def adapt_detection_prob(self, timestamp):
        """
        Parameters we have to consider:
            - current number of targets (estimated)
            - prob. for a false alarm
            - classification?
            - expected number of new targets since last update step

        Effects:
            - low detection probability: - prior hypotheses weights will not decrease to much
                                         - if we can associate bearing --> estimated number of targets will increase
                                         - can deal with false alarms

            - high detection probability: - prior hypotheses weights will decrease and eventually will be pruned
                                          - if we associate bearing --> estimate number of targets will not increase to much
                                          - can not deal with false alarms

            - multiple targets with same class: - cause why we cant use just the classification prob.
                                                - example: 2 Targets with class A and class. prob.: 0.9
                                                - if we set p_D = 0.9 then the priors weights will decrease and
                                                  we will assume that we only have one target
                                                - actually p_D should be something like < 0.45


        """
        p_false_alarm = 0.5
        # number of new targets + number of past targets that were removed because of too low weights
        # we have to assume that we will loose a few targets between two updates, because of our low update rate
        # it depends on the true number of target and the time between updates

        #time_since_last_update = timestamp - self.last_update_time
        n = self.n_targets + p_false_alarm
        prob = 1.0/n

        return prob

    def generate_measurement_hypothesis(self, timestamp, Z, classification):
        """
        Initialized a new set of Gaussian mixture, each corresponds to one possible
        classification.
        :param Z: set of measurements - generated by 'bearing_to_measurements'
        :param classification: classification vector non-normalized
        :return: set of new hypothesis representing a possible new target
        """
        new_hypothesis = []

        # normalize weight of measurement w.r.t. to covariance area
        meas_w = [np.linalg.det(z.R) for z in Z]
        meas_w = meas_w / np.sum(meas_w)

        # total prob. that the set of new generated GM is a target
        p_birth = self.model.measurement_hypo_w

        """
        @todo: in the initialization of a new GM we should consider the classification 
            - if we always just assume that the bearing is max. one target we will have problems in
              scenarios with multiple targets since the update rate for each target is very low 
              --> weights of long non-seen targets decrease more than the weight of a new GM
            
            BUT: We also have to consider the current estimate o/w our new GM have to large weights and
            represents too many new targets
            
            - need a new parameter that somehow describes that a new target is initialized or that
              we have (possibly) multiple targets of one class
       
        """

        classification = classification/np.sum(classification)
        sum_w = 0.0
        for i in range(0, len(classification)):
            # classification prob.
            p_c = classification[i]
            for j in range(len(Z)):
                # weight for a specific measurement
                z_w = meas_w[j]
                x = Z[j].x
                P = Z[j].R
                cl = i
                w = z_w * p_c * p_birth

                sum_w += w
                new_hypothesis.append(Hypothesis(timestamp, w, x, P, cl))

        return new_hypothesis

    def number_of_targets_per_class(self, hypothesis):
        """
        Computes the number of targets per class based on the current hypotheses.
        The number of targets is given by the sum over the weights.
        :param hypothesis: list of current hypothesis
        :return: total number of targets, list of number of targets per class
        """
        n_targets_classes = np.zeros(self.model.n_bird_classes)

        for hypo in hypothesis:
            n_targets_classes[hypo.classification] += hypo.w

        return sum(n_targets_classes), n_targets_classes

    def bearing_to_measurements(self, bearing):
        """
        transforms an one dimensional bearing to a set of measurements
        :param bearing: bearing as angle in radians
        :return: list of measurements
        """
        Z = []
        stepsize = self.model.max_range / self.model.N
        ranges = np.arange(stepsize, self.model.max_range + stepsize, stepsize)

        rotation_mat = np.array([[cos(bearing.angle), -sin(bearing.angle)],
                                 [sin(bearing.angle), cos(bearing.angle)]])

        for r in ranges:
            measurement = np.array([r * cos(bearing.angle), r * sin(bearing.angle)]) + bearing.position
            theta = np.array([[np.power(self.model.max_range / (4 * self.model.N), 2), 0],
                              [0, np.power(r * bearing.sigma, 2)]])

            R = rotation_mat @ theta @ transpose(rotation_mat)
            Z.append(Measurement(measurement, R))

        return Z

    def pruning(self, hypothesis):
        """
        Deletes all hypothesis with a weight smaller than some threshold defined by the model
        :param hypothesis: current list of hypothesis
        :return: pruned list of hypothesis
        """
        new_hypothesis = [hypo for hypo in hypothesis if hypo.w >= self.model.prune_threshold]
        return new_hypothesis

    def merge_hypothesis(self, hypothesis):
        """
        Merges similar hypothesis if there 'Mahalanobis Norm' (similarity) is smaller than some
        threshold U and the classification is the same
        :param hypothesis: list of current hypothesis
        :return: list of merged hypothesis
        """
        I = copy.deepcopy(hypothesis)
        new_hypothesis = []
        U = self.model.merge_threshold
        while I:
            j = np.argmax([hypo.w for hypo in I])
            L = [hypo for hypo in I if self.dist_between_hypos(hypo, I[j]) <= U
                                    and hypo.classification == I[j].classification]
            I = [hypo for hypo in I if hypo not in L]

            timestamp = L[0].timestamp
            w = np.sum(hypo.w for hypo in L)
            x = 1.0 / w * np.sum([hypo.w * hypo.x for hypo in L], axis=0)

            P = np.zeros((2, 2))
            for hypo in L:
                P += hypo.w * (hypo.P + (x - hypo.x) @ transpose(x - hypo.x))
            P = 1.0 / w * P

            new_hypothesis.append(Hypothesis(timestamp, w, x, P, L[0].classification))

        return new_hypothesis

    @staticmethod
    def dist_between_hypos(hypo1, hypo2):
        """
        Distance between two hypothesis ~ Similarity
        """
        return transpose(hypo1.x - hypo2.x) @ inv(hypo1.P) @ (hypo1.x - hypo2.x)
