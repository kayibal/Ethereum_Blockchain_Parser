import numpy as np
import pandas as pd
from ethex.analysis.txn_graph import TxnGraph


def make_quantiles(key, s):
    if not isinstance(s, pd.Series):
        s = pd.Series(s)
    key = key + '_{}'
    quantiles = s.quantiles(np.linspace(0.1, 1, 10))
    return quantiles.index.map(key.format).todict()

def parse_graph(g: TxnGraph):
    out_flow = g.txn_mat._data.sum(axis=1)
    in_flow = g.txn_mat._data.sum(axis=0)
    out_flow_bin = (g.txn_mat._data > 0).sum(axis=1)
    in_flow_bin = (g.txn_mat._data > 0).sum(axis=0)
    data = {
        'ts': g.start_timestamp,
        'txn_volume': g.txn.shape[0],
        'contract_volume': g.contract_map.shape[0],
        'max_transaction_value': g.txn.max(),
        'mean_transaction_value': g.txn.mean(),
        'mean_transaction_std': g.txn.std(),
        'median_transaction_value': g.txn.median(),
        'out_flow_median': out_flow.median(),
        'out_flow_mean': out_flow.mean(),
        'out_flow_std':  out_flow.std(),
        'out_degree_median': out_flow_bin.median(),
        'out_degree_mean': out_flow_bin.mean(),
        'out_degree_std': out_flow_bin.std(),
        'in_flow_median': in_flow.median(),
        'in_flow_mean': in_flow.mean(),
        'in_flow_std': in_flow.std(),
        'in_degree_median': in_flow_bin.median(),
        'in_degree_mean': in_flow_bin.mean(),
        'in_degree_std': in_flow_bin.std(),
    }
    quantiles = {
        'out_flow': out_flow,
        'in_flow': in_flow,
        'out_degree': out_flow_bin,
        'in_degree': in_flow_bin,
        'txn': g.txn,
        'eth': g.eth,
    }
    for key, s in quantiles.items():
        key += '_uantiles'
        data.update(make_quantiles(key, s))
