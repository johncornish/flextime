#! /usr/bin/env python3
import yaml, os, re, dateutil.parser, click
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
            ' '.join([str(n) for n in self.name_path]),
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
            self.leaves = self.extract_leaves()

    def save(self):
        output = yaml.dump(self.dtree)
        print(output)
        with open(self.datafile, 'w') as f:
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


@click.group()
@click.option('-f', default='tasks.yml')
@click.pass_context
def cli(ctx, f):
    ctx.obj = FlexTime(f)

@cli.command()
@click.argument('sort_keys', nargs=-1)
@click.option('--lim', default=-1)
@click.pass_obj
def todo(ft, sort_keys, lim):
    def todo_str(todos):
        return "\n\n".join(['[{}] {}'.format(i, str(t)) for i, t in todos[:lim]])

    def show_todos():
        if len(sort_keys) > 0:
            todos = ft.multisorted(sort_keys)
        else:
            todos = ft.leaf_tuples()

        os.system('clear')
        print(todo_str(todos))
        
    while True:
        show_todos()
        cind = input("Complete [<i>/w/Q]: ")

        if cind.isdigit():
            ft.complete_task(int(cind))
        else:
            if cind == 'w':
                ft.save()
            break
            

if __name__ == '__main__':
    cli()
