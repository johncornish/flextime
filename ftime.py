import yaml, re

def leaves(data, names = [], attributes = {}):
    children = [(k,v) for k, v in data.items() if not re.match("^_.*", str(k))]
    these_attributes = {k: v for k, v in data.items() if re.match("^_.*", str(k))}

    if len(children) > 0:
        for name, c in children:
            yield from leaves(c, names + [name], dict(attributes, **these_attributes))
    else:
        yield (' '.join([str(n) for n in names]), dict(attributes, **these_attributes))

def multisort(lvs, *keys):
    return sorted(lvs, key = lambda x: [x[1].get(attr, 0) for attr in keys])

with open('data.yml') as f:
    d = yaml.safe_load(f)
    lvs = leaves(d)
    [print(i) for i in list(multisort(lvs, '_t', '_d'))]
