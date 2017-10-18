import yaml, re, dateutil.parser
from os.path import isfile
from datetime import datetime, date
from functools import reduce

class TaskLeaf:
    def date_to_str(d):
        date_format = '%m-%d-%Y'
        return d.strftime(date_format)
        
    def __init__(self, path, data):
        self.path = path
        self.data = data

    def __str__(self):
        if '_d' in self.data:
            due_str = TaskLeaf.date_to_str(dateutil.parser.parse(self.data.get('_d')))
        else:
            due_str = 'No due date'

        return '({}) {} - {} mins'.format(
            due_str,
            ' > '.join([str(n) for n in self.path]),
            self.data.get('_t', 0)
        )

    def toordinal(self, attrs):
        def get_ord(attr):
            val = 0
            attr_key = '_' + re.sub('\^', '', attr)
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
            self._datatree = TaskTree.file_to_dict(self._datafile)
        else:
            print("{} not found. It will be created on save.".format(self._datafile))
            self._datatree = {}

    def dump_dict(d):
        return yaml.dump(d, default_flow_style=False)
    
    def file_to_dict(filename):
        if isfile(filename):
            with open(filename) as f:
                return yaml.safe_load(f)
        else:
            print("{} not found; skipping.".format(filename))
            
    def tree(self):
        return self._datatree
    
    def save(self):
        self.normalize_tree()
        output = str(self)
        with open(self._datafile, 'w') as f:
            f.write(output)

    def __str__(self):
        return TaskTree.dump_dict(self._datatree)

    def sorted_leaves(self, sort_keys):
        return sorted(self.leaves(), key = lambda x: x.toordinal(sort_keys))
        
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
        def normalize_props(path):
            failed_props = []
            props = self.props_from_path(path)
            if len(props) > 0:
                if '_d' in props:
                    due_date = props['_d']
                    if due_date == 'today':
                        due_date = datetime.today()
                    elif isinstance(due_date, date):
                        due_date = due_date
                    else:
                        try:
                            due_date = dateutil.parser.parse(due_date)
                            props['_d'] = TaskLeaf.date_to_str(due_date)
                        except ValueError:
                            failed_props.append('_d')

                if '_t' in props:
                    time = props['_t']
                    if isinstance(time, str) and not time.isdigit():
                        failed_props.append('_t')
                    else:
                        props['_t'] = int(time)

                current_branch = self.branch_from_path(path)
                for p in failed_props:
                    print("Failed to normalize value '{}' of property '{}' at '{}'; dropping.".format(str(props[p]), p, ' > '.join(map(str, path))))
                    del props[p]
                    del current_branch[p]

                current_branch.update(props)

        def recursive_normalize(paths):
            for path in paths:
                normalize_props(path)
                    
                sub_keys = self.keys_from_path(path)
                if len(sub_keys) > 0:
                    recursive_normalize([path + [k] for k in sub_keys])
                    
        recursive_normalize([[]])
       
    def props_from_path(self, path):
        return {k: v for k, v in self.branch_from_path(path).items() if re.match('^_.*', str(k))}

    def keys_from_path(self, path):
        return [k for k in self.branch_from_path(path).keys() if not re.match('^_.*', str(k))]
                    
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
                print(str(self))

    def branch_from_path(self, path):
        node = self._datatree
        for p in path:
            if p not in node:
                node[p] = {}

            node = node[p]

        return node
