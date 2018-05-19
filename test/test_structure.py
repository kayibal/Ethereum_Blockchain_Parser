from pathlib import Path

from ethex.structure import FileStructure
from datetime import datetime

def test_structure():
    PATH = FileStructure(
        ROOT=Path(__file__).parents[1],
        LOGDIR='logs',
        MONGO_DB=('data', 'mongo'),
        BC_DATA=('data', 'bc'),
        ARTEFACT=('data', 'artefacts', '{:%Y-%m-%d}.tar.gz')
    )
    assert PATH.__repr__()
    assert PATH.format('ARTEFACT', datetime(2000, 1, 1)) == \
        Path('/Users/kayibal/code/eth_blockchain_extractor/data/artefacts/2000-01-01.tar.gz')
