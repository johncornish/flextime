import yaml, re

def leaves(data, names = [], attributes = {}):
    children = [(k,v) for k, v in data.items() if not re.match("^_.*", str(k))]
    these_attributes = {k: v for k, v in data.items() if re.match("^_.*", str(k))}

    if len(children) > 0:
        for name, c in children:
            yield from leaves(c, names + [name], dict(attributes, **these_attributes))
    else:
        yield (' '.join([str(n) for n in names]), dict(attributes, **these_attributes))

with open('data.yml') as f:
    d = yaml.safe_load(f)
    lvs = leaves(d)
    [print(i) for i in list(lvs)]
