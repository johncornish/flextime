import yaml
from os.path import isfile

class TaskTree:
    def __init__(self, datafile=False):
        if not datafile:
            self._datafile = "tasks.yml"
        else:
            self._datafile = datafile

        if isfile(self._datafile):
            with open(self._datafile) as f:
                self._datatree = yaml.safe_load(f)
        else:
            print("I will write to {} on save".format(self._datafile))
            self._datatree = {}

    def save(self):
        output = yaml.dump(self._datatree)
        with open(self._datafile, 'w') as f:
            f.write(output)

    def add_branch(self, path, data):
        node = self.branch_from_path(path)
        node.update(data)

    def branch_from_path(self, path):
        node = self._datatree
        for p in path:
            if p not in node:
                node[p] = {}

            node = node[p]

        return node
