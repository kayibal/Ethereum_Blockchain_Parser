from pathlib import Path
from tree_format import format_tree
from operator import attrgetter


class FileNode(object):
    def __init__(self, children=(), id=None):
        self.children = set(children)
        self.id = id
        self.key = None

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return str(self.id)

    @property
    def label(self):
        if self.key is None:
            return str(self.id.stem)
        else:
            return '{} [{}]'.format(self.id.stem, self.key)


class FileStructure(dict):

    def __init__(self, ROOT, *args, **kwargs):
        super(FileStructure, self).__init__(*args, **kwargs)
        if not isinstance(ROOT, Path):
            ROOT = Path(ROOT)

        self._tree = FileNode(id=ROOT)
        self._tree.key = 'ROOT'
        self._nodes = {}
        self['ROOT'] = self.ROOT = ROOT.absolute()
        for key, value in self.items():
            if key != 'ROOT':
                self.__setitem__(key, value)

    def __setitem__(self, key, value):
        if isinstance(value, tuple):
            value = Path(*value)
        if not isinstance(value, Path):
            value = Path(value)

        if key != 'ROOT':
            self._insert_into_tree(key, value)

        super(FileStructure, self).__setitem__(key, value)

    def _insert_into_tree(self, key, value):
        cur_node = self._tree
        ids = list(value.parents)[:-1][::-1] + [value]
        for id in ids:
            node = self._get_node(id)
            if id == ids[-1]:
                node.key = key
            cur_node.children.add(node)
            cur_node = node

    def _get_node(self, id):
        try:
            return self._nodes[id]
        except KeyError:
            node = FileNode(id=id)
            self._nodes[id] = node
            return node

    def make_repr(self, node):
        label = node.id.stem
        if not node.children:
            children = []
        else:
            children = [self.make_repr(n) for n in node.children]
        return label, children

    def __repr__(self):
        return format_tree(self._tree, format_node=attrgetter('label'),
                           get_children=attrgetter('children'))

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
