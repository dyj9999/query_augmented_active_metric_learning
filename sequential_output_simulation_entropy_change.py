# -*- coding: utf-8 -*-
"""
Run a single replication of simulation.

AQM + MEE

@author: Yujia Deng
"""

from sequential_output_npu import *
import sys
import os
import errno

sys.argv = ['', 5, 30, 3, 60, 10, 0]
#############
_, P1, P2, mu, N_per_cluster, max_nc, rep = sys.argv
#############

P1 = int(P1)
P2 = int(P2)
N_per_cluster = int(N_per_cluster)
mu = float(mu)
max_nc = int(max_nc)
rep = int(rep)

request_nc = range(10, max_nc+1, 10)

np.random.seed(rep)
save_path = './results_collection/simulation_high_dim_4/P1_%d_P2_%d_mu_%2.1f_N_per_cluster_%d/max_nc_%d/' % (P1, P2, mu, N_per_cluster, max_nc)
print(save_path)
print('rep=%d' % rep)

if not os.path.exists(save_path):
    try:
        os.makedirs(save_path, 0o700)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


X0, y, K, num_per_class, scale = load_high_dim4(P1, P2, N=N_per_cluster, mu=mu, seed=rep)
A0 = np.random.randn(P1+P2, P1+P2)
A0 = A0@A0.T
X = transform(X0, A0)

result_proposed_no_penalty, result_proposed_penalty, A_hist, A_hist_penalize = ARI_active(metric_learn_method='proposed', X=X, y=y, K=K, max_nc=max_nc, impute_method='default', weighted=True, uncertainty='random_forest',diag=True, true_H=False, include_H=True, lambd=1000, gamma=100, rank=1, num_p=int(P2/2), verbose=None, penalized=True, initial='default', request_nc=request_nc)

###########
# For COBRA
###########
n_super_instances = range(10, 300, 20)
result_COBRA = dict()
for nsi in n_super_instances:
    ARI, n_query = ARI_nc_COBRA(X, y, K, nsi)
    result_COBRA[nsi] = (n_query, ARI)


np.savez(os.path.join(save_path, ('rep%d.npz' % rep)),result_proposed_no_penalty=result_proposed_no_penalty, result_proposed_penalty=result_proposed_penalty, result_COBRA=result_COBRA, A_hist=A_hist, A_hist_penalize=A_hist_penalize)

print(result_proposed_no_penalty)
print(result_proposed_penalty)
print(result_COBRA)

