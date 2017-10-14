import yaml, os, re, dateutil.parser
from functools import reduce
from datetime import datetime

class TaskLeaf:
    def __init__(self, names, data):
        self.name_path = names
        self.data = data

    def __str__(self):
        date_format = "%m-%d-%y"
        if '_d' in self.data:
            due_date = dateutil.parser.parse(self.data.get('_d'))
        else:
            due_date = datetime.today()
            
        return '({}) {} - {}'.format(
            due_date.strftime(date_format),
            ' | '.join([str(n) for n in self.name_path]),
            self.data.get('_t', 0)
        )

    def to_ord(self, attrs):
        def get_ord(attr):
            val = 0
            attr_key = '_' + re.sub('_', '', attr)
            if attr_key in self.data:
                if attr_key == '_d':
                    val = dateutil.parser.parse(self.data.get('_d')).toordinal()
                else:
                    val = self.data.get(attr_key)

                if re.match('^_.*', str(attr)):
                    val = -val

            return val
            
        return list(map(get_ord, attrs))
        

class FlexTime:
    def __init__(self, data_file):
        self.datafile = data_file
        with open(data_file) as f:
            self.dtree = yaml.safe_load(f)
            #print(yaml.dump(self.dtree))
            self.leaves = self.extract_leaves()

    def save(self):
        output = yaml.dump(self.dtree)
        with open(self.datafile, 'w') as f:
            print(output)
            f.write(output)

    def extract_leaves(self):
        def rfind_leaves(data, names = [], attributes = {}):
            children = [(k,v) for k, v in data.items() if not re.match("^_.*", str(k))]
            these_attributes = {k: v for k, v in data.items() if re.match("^_.*", str(k))}

            if len(children) > 0:
                for name, c in children:
                    yield from rfind_leaves(c, names + [name], dict(attributes, **these_attributes))
            else:
                yield TaskLeaf(names, dict(attributes, **these_attributes))

        return list(rfind_leaves(self.dtree))

           
    def complete_task(self, task_ind):
        to_remove = self.dtree
        np = self.leaves.pop(task_ind).name_path
        for p in np[:-1]:
            to_remove = to_remove[p]

        del to_remove[np[-1]]
        
    def leaf_tuples(self):
        return [(i, l) for i, l in enumerate(self.leaves)]

    def multisorted(self, keys):
        return sorted(self.leaf_tuples(), key = lambda x: x[1].to_ord(keys))

    def node_from_path(path):
        node = self.dtree
        for p in path:
            node = node[p]

        return node

    def guess_path(self, args):
        def build_path(acc, word):
            tree, path_parts = acc

            path_parts[-1].append(word)

            key = ' '.join(path_parts[-1])
            if key in tree:
                tree = tree[key]
                path_parts.append([])

            return (tree, path_parts)
        return reduce(build_path, args, (self.dtree, [[]]))
