from pathlib import Path


class FileStructure(dict):

    def __init__(self, ROOT, *args, **kwargs):
        super(FileStructure, self).__init__(*args, **kwargs)
        if not isinstance(ROOT, Path):
            ROOT = Path(ROOT)

        self['ROOT'] = self.root = ROOT.absolute()
        for key, value in self.items():
            if key != 'ROOT':
                self.__setitem__(key, value)

    def __setitem__(self, key, value):
        if isinstance(value, tuple):
            value = Path(*value)
        if not isinstance(value, Path):
            value = Path(value)
        super(FileStructure, self).__setitem__(key, value)

    def __getitem__(self, key):
        rel_path = super(FileStructure, self).__getitem__(key)
        path = self.ROOT / rel_path
        dir_ = path
        if path.suffix:
            dir_ = path.parents[0]
        dir_.mkdir(parents=True, exist_ok=True)
        return path

    def format(self, key, *args, **kwargs):
        str_path = str(self.__getitem__(key))
        return Path(str_path.format(*args, **kwargs))


PATH = FileStructure(
    ROOT=Path(__file__).parents[1],
    LOGDIR='logs',
    MONGO_DB=('data', 'mongo'),
    BC_DATA=('data', 'bc')
)