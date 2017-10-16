import yaml, re, dateutil.parser
from os.path import isfile
from datetime import datetime
from functools import reduce

class TaskLeaf:
    def __init__(self, path, data):
        self.path = path
        self.data = data

    def __str__(self):
        date_format = "%m-%d-%y"
        if '_d' in self.data:
            due_date = dateutil.parser.parse(self.data.get('_d'))
        else:
            due_date = datetime.today()

        return '({}) {} - {}'.format(
            due_date.strftime(date_format),
            ' | '.join([str(n) for n in self.path]),
            self.data.get('_t', 0)
        )

    def toordinal(self, attrs):
        def get_ord(attr):
            val = 0
            attr_key = '_' + re.sub('^', '', attr)
            if attr_key in self.data:
                if attr_key == '_d':
                    val = dateutil.parser.parse(self.data.get('_d')).toordinal()
                else:
                    val = self.data.get(attr_key)

                if re.match('^\^.*', str(attr)):
                    val = -val

            return val
            
        return list(map(get_ord, attrs))

    
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
            print("{} not found. It will be created on save.".format(self._datafile))
            self._datatree = {}

    def save(self):
        output = self.dump()
        with open(self._datafile, 'w') as f:
            f.write(output)

    def dump(self):
        return yaml.dump(self._datatree)

    def leaves(self):
        def recursive_find(data, path = [], attrs = {}):
            children = [(k,v) for k, v in data.items() if not re.match("^_.*", str(k))]
            new_attrs = dict(attrs, **{k: v for k, v in data.items() if re.match("^_.*", str(k))})

            if len(children) > 0:
                for key, child in children:
                    yield from recursive_find(child, path + [key], new_attrs)
            else:
                yield TaskLeaf(path, new_attrs)

        return list(recursive_find(self._datatree))

    def normalize_tree(self):
        pass
        
    def keys_from_path(self, path):
        return list(self.branch_from_path(path).keys())
                    
    def merge_branch(self, path, data):
        node = self.branch_from_path(path)
        node.update(data)
        self.normalize_tree()

    def delete_branch(self, path):
        node = self.branch_from_path(path[:-1])
        if len(path) >= 1:
            delete_key = path[-1]
            if delete_key in node:
                del node[delete_key]
            else:
                print("{} not found in tree:".format(' > '.join(map(str, path))))
                print(self.dump())

    def branch_from_path(self, path):
        node = self._datatree
        for p in path:
            if p not in node:
                node[p] = {}

            node = node[p]

        return node
