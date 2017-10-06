import yaml, re, dateutil.parser
from functools import reduce

def str_to_date(leaf):
    attrs = leaf.get('attrs')
    if '_d' in leaf['attrs']:
        attrs['_d'] = dateutil.parser.parse(attrs.get('_d'))

    return dict(leaf, attrs = attrs)

def add_ordinality(leaf):
    ordattrs = dict(leaf.get('attrs'))
    if '_d' in ordattrs:
        ordattrs.update({'_d': dateutil.parser.parse(ordattrs.get('_d')).toordinal()})

    return dict(leaf, ordattrs = ordattrs)

class FlexTime:
    def extract_leaves(self):
        def rfind_leaves(data, names = [], attributes = {}):
            children = [(k,v) for k, v in data.items() if not re.match("^_.*", str(k))]
            these_attributes = {k: v for k, v in data.items() if re.match("^_.*", str(k))}

            if len(children) > 0:
                for name, c in children:
                    yield from rfind_leaves(c, names + [name], dict(attributes, **these_attributes))
            else:
                yield {'names': names, 'attrs': dict(attributes, **these_attributes)}

        self.leaves = list(rfind_leaves(self.dtree))

    def mmap(self, *funcs):
        def apply_func(acc, f):
            return map(f, acc)
        
        return list(reduce(apply_func, funcs, self.leaves))
        
    def __init__(self, data_file_name):
        with open(data_file_name) as f:
            self.dtree = yaml.safe_load(f)
            self.extract_leaves()

    
def multisort(lvs, *keys):
    return sorted(lvs, key = lambda x: [x['ordattrs'].get(attr, 0) for attr in keys])

[print(l) for l in multisort(FlexTime('data.yml').mmap(add_ordinality), '_d', '_t')]
