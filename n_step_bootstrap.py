from typing import Iterable, Tuple
import numpy as np


def init_q(s, a, type="ones"):
    """
    @param s the number of states
    @param a the number of actions
    @param type random, ones or zeros for the initialization
    """
    if type == "ones":
        return np.ones((s, a))
    elif type == "random":
        return np.random.random((s, a))
    elif type == "zeros":
        return np.zeros((s, a))


def on_policy_n_step_td(
        gamma,
        trajs: Iterable[Iterable[Tuple[int, int, int, int]]],
        n: int,
        alpha: float,
        initV: np.array
) -> Tuple[np.array]:
    """
    input:
        env_spec: environment spec
        trajs: N trajectories generated using
            list in which each element is a tuple representing (s_t,a_t,r_{t+1},s_{t+1})
        n: how many steps?
        alpha: learning rate
        initV: initial V values; np array shape of [nS]
    ret:
        V: $v_pi$ function; numpy array shape of [nS]
    """

    #####################
    # TODO: Implement On Policy n-Step TD algorithm
    # sampling (Hint: Sutton Book p. 144)
    #####################

    # gamma = env_spec.gamma
    V = initV

    for traj in trajs:
        T = len(traj)
        for t in range(T):

            # update state estimate at time tau
            tau = t - n + 1
            if tau >= 0:
                G = 0
                # WHY START FROM TAU + 1 IN THE BOOK?
                for i in range(tau, min(tau + n, T)):
                    G += np.power(gamma, i - tau) * traj[i][2]
                if tau + n < T:
                    G += np.power(gamma, n) * V[traj[tau + n][0]]
                V[traj[tau][0]] += alpha * (G - V[traj[tau][0]])

    return V


class GreedyPolicy(object):
    def __init__(self, Q):
        self._Q = Q

    def action_prob(self, state: int, action: int) -> float:
        if self.action(state) == action:
            return 1
        else:
            return 0

    def action(self, state: int) -> int:
        return np.argmax(self._Q[state, :])


class epsilon_greedy(object):
    def __init__(self, Q, epsilon):
        self.probability = np.random.rand()
        self.Q = Q
        self.epsilon = epsilon

    def action_prob(self, state: int, action: int) -> float:
        target_action = self.action(state)
        if target_action == action:
            return self.epsilon + self.probability / len(self.Q[state])
        else:
            return self.probability / len(self.Q[state])

    def action(self, state: int) -> int:
        k_actions = len(self.Q[state])
        if self.probability < self.epsilon:
            select_greedy_action = np.argmax(self.Q[state, :])
            return select_greedy_action
        select_action_randomly = np.random.choice(k_actions)
        return select_action_randomly


def off_policy_n_step_sarsa(
        gamma: float,
        trajs: Iterable[Iterable[Tuple[int, int, int, int]]],
        bpi,
        nS,
        nA,
        n: int,
        alpha: float,
        epsilon=0.9
):
    """
    input:
        env_spec: environment spec
        trajs: N trajectories generated using
            list in which each element is a tuple representing (s_t,a_t,r_{t+1},s_{t+1})
        bpi: behavior policy used to generate trajectories
        pi: evaluation target policy
        n: how many steps?
        alpha: learning rate
        initQ: initial Q values; np array shape of [nS,nA]
    ret:
        Q: $q_star$ function; numpy array shape of [nS,nA]
        policy: $pi_star$; instance of policy class
    """

    #####################
    # TODO: Implement Off Policy n-Step SARSA algorithm
    # sampling (Hint: Sutton Book p. 149)
    #####################

    Q = init_q(nS, nA, type="zeros")
    # pi = GreedyPolicy(Q)
    pi = epsilon_greedy(Q, epsilon)
    timestep_reward = []

    for traj in trajs:
        T = len(traj)
        total_reward = 0
        for t in range(T):
            tau = t - n + 1
            total_reward += traj[t][2]
            if tau >= 0:
                rho = 1
                # for i in range(tau, min(tau+n-1, T-1)):
                for i in range(tau + 1, min(tau + n, T)):
                    rho *= (pi.action_prob(traj[i][0], traj[i][1]) / bpi.action_prob(traj[i][0], traj[i][1]))
                G = 0
                for i in range(tau, min(tau + n, T)):
                    G += np.power(gamma, i - tau) * traj[i][2]
                if tau + n < T:
                    G += np.power(gamma, n) * Q[traj[int(tau + n)][0], traj[int(tau + n)][1]]

                Q[traj[int(tau)][0], traj[int(tau)][1]] += alpha * rho * (G - Q[traj[int(tau)][0], traj[int(tau)][1]])

        timestep_reward.append(total_reward)

    # pi = GreedyPolicy(Q)
    pi = epsilon_greedy(Q, epsilon)

    return Q, timestep_reward, pi
