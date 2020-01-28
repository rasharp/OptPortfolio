import numpy as np
import cvxopt as opt
from cvxopt import solvers, blas

"""
Use internal CVXOPT type of matricies
"""


def opt_port(rets, ret_lim, annualize=252):
    n = rets.shape[0]
    means = np.mean(rets, axis=1) * annualize

    # f = 0.5 * w *'COV* w + q'*w
    P = opt.matrix(np.cov(rets)) * annualize
    q = opt.matrix(np.zeros((n, 1)))

    # w >= 0
    G = opt.matrix(-np.eye(n))
    h = opt.matrix(np.zeros((n, 1)))

    # sum(w) = 1, ret*w = ret_lim
    A = opt.matrix(np.vstack((np.ones((1, n)), means)))
    b = opt.matrix(np.array([[1], [ret_lim]]))

    # Calculate efficient frontier weights using quadratic programming
    x = solvers.qp(P, q, G, h, A, b)['x']  # return cxopt.matrix

    ## CALCULATE RISKS AND RETURNS FOR FRONTIER
    pret = blas.dot(opt.matrix(means), x)  # means.T * x
    prisk = np.sqrt(blas.dotu(x, P * x))  # x.T * P * x
    return np.array(x), pret, prisk


def opt_port_gmv(rets, annualize=252):
    n = rets.shape[0]
    means = np.mean(rets, axis=1) * annualize

    # f = 0.5 * w *'COV* w + q'*w
    P = opt.matrix(np.cov(rets)) * annualize
    q = opt.matrix(np.zeros((n, 1)))

    # w >= 0
    G = opt.matrix(-np.eye(n))
    h = opt.matrix(np.zeros((n, 1)))

    # sum(w) = 1, ret*w = ret_lim
    A = opt.matrix(np.ones((1, n)))
    b = opt.matrix(np.ones((1, 1)))

    # Calculate efficient frontier weights using quadratic programming
    x = solvers.qp(P, q, G, h, A, b)['x']  # return cxopt.matrix

    ## CALCULATE RISKS AND RETURNS FOR FRONTIER
    pret = blas.dot(opt.matrix(means), x)  # means.T * x
    prisk = np.sqrt(blas.dotu(x, P * x))  # x.T * P * x
    return np.array(x), pret, prisk


# Maximize Sharpe ratio based on efficient frontier (efp)
def max_sharpe(efpw, efp_rets, efp_std, rfrate):
    sratios = list(map(lambda r, s: (r-rfrate)/s, efp_rets, efp_std))
    k_opt = np.argmax(sratios)
    return efpw[k_opt], efp_rets[k_opt], efp_std[k_opt]


# Random portfolio
def random_portfolio(means, cov):
    p = np.asmatrix(means)
    rp = np.random.rand(len(means))
    rp /= sum(rp)

    w = np.asmatrix(rp)
    C = np.asmatrix(cov)

    mu = w * p.T  # Portfolio return
    sigma = np.sqrt(w * C * w.T)  # Portfolio sigma
    hhi = sum((np.array(w) ** 2)[0])
    return mu[0, 0], sigma[0, 0], hhi


# Initialization
solvers.options['show_progress'] = False  # disable notifications about optimization progress
