import yaml, re

def leaves(data, names = []):
    children = [(k,v) for k, v in data.items() if not re.match("^_.*", str(k))]
    if len(children) > 0:
        for name, c in children:
            yield from leaves(c, names + [name])
    else:
        yield (' '.join([str(n) for n in names]), data)

with open('data.yml') as f:
    d = yaml.safe_load(f)
    lvs = leaves(d)
    [print(i) for i in list(lvs)]
