"""Create a snapshot of the Ethereum network."""
import json
from functools import lru_cache

import pandas as pd
import sparsity as sp
import toolz
from scipy.sparse import csr_matrix
from ethex.crawler.util import getClient


def _sparse_frame_from_multiindex(values):
    """Create a sparse matrix from a pandas.Series with MultiIndex."""
    assert isinstance(values.index, pd.MultiIndex)
    midx = values.index

    # MulitIndex is already categorical label encode i,j positions of data
    data_matrix = csr_matrix((values.values, (midx.labels[0], midx.labels[1])))
    sf = sp.SparseFrame(data_matrix,
                        index=midx.levels[0],
                        columns=midx.levels[1])
    return sf

class TxnGraph(object):

    def __init__(self, start, end):
        self.start_block = start
        self.end_block = end

        self.contract_map = None
        self.txn = None
        self.eth = None

        self.start_timestamp = None
        self.end_timestamp = None

    def extract(self):
        client = getClient()
        self._update_ts(client)
        self._extract_timerange(self.start, self.end, client)

    def _update_ts(self, client):
        """Lookup timestamps associated with start/end blocks and set them."""
        start = client.find_one({"number": self.start_block})
        end = client.find_one({"number": self.end_block})
        self.start_timestamp = start["timestamp"]
        self.end_timestamp = end["timestamp"]
        return client

    def _extract_timerange(self, start, end, client):
        blocks = client.find(
            {"number": {"$gt": start, "$lt": end}},
        )

        contract_maps, data = zip(*map(self._transform_block, blocks))
        self.contract_map = pd.concat(contract_maps).drop_duplicates()
        txn = pd.concat(data)
        self.txn = txn.groupby(levels=[0, 1]).sum()
        self.eth = txn.groupby(level=1).sum()

    def _transform_block(self, block):
        txn_keys = {'to', 'from', 'data', 'value'}
        txn = pd.DataFrame.from_records(
            toolz.keyfilter(lambda x: x in txn_keys, block['transactions'])
        )
        txn = txn.loc[txn['to'] != txn['from']]
        contract_map = txn.dropna('data')
        contract_map = contract_map.loc[contract_map.data != '0x', 'to']
        data = txn['from', 'to', 'value'].groupby(['from', 'to']).sum()
        return contract_map, data

    def save(self, outdir):
        paths = self._make_paths(outdir)
        with outdir.joinpath('_metadata').open('wb') as fp:
            fp.write(json.dumps(
                start=self.start_block,
                end=self.end_block,
                start_timestamp=self.start_timestamp,
                end_timestamp=self.end_timestamp
            ))
        self.txn.to_pickle(paths['txn'])
        self.eth.to_pickle(paths['eth'])
        self.contract_map.to_pickle(paths['contract_map'])

    @property
    @lru_cache(maxsize=1)
    def txn_mat(self):
        return _sparse_frame_from_multiindex(self.txn)

    @property
    @lru_cache(maxsize=1)
    def contract_mat(self):
        contract_txn = self.txn_mat.loc[self.contract_map.tolist(),
                                        self.contract_map.tolist()]
        return _sparse_frame_from_multiindex(contract_txn)

    @staticmethod
    def _make_paths(outdir):
        return {
            'txn': outdir.joinpath('txn.pickle.gz'),
            'eth': outdir.joinpath('eth.pickle.gz'),
            'contract_map': outdir.joinpath('contract_map.pickle.gz'),
            'metadata': outdir.joinpath('_metadata')
        }

    @classmethod
    def load(cls, outdir):
        paths = cls._make_paths(outdir)
        with outdir.join('_metadata').open('rb') as fp:
            metadata = json.load(fp)

        start, end = metadata.pop('start', 'end')
        obj = cls(start, end)
        obj.txn = pd.read_pickle(paths['txn'])
        obj.eth = pd.read_pickle(paths['eth'])
        obj.contract_map = pd.read_pickle(paths['contract_map'])
        return obj
