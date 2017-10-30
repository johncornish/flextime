import networkx as nx, dateutil.parser

from flextime import utils
from functools import reduce
from datetime import datetime

class TimeBlock:
    def __init__(self, data):
        required_keys = ['day', 'name', 'start', 'end', 'resource_order']
        if all([k in data for k in required_keys]):
            for k, v in data.items():
                setattr(self, k, v)
        else:
            print('Missing required attributes in TimeBlock')
            exit(1)

    def __str__(self):
        return "{} {}: {}-{} ({})".format(
            self.day,
            self.name,
            '{:02d}:{:02d}'.format(*divmod(self.start, 60)),
            '{:02d}:{:02d}'.format(*divmod(self.end, 60)),
            self.num_minutes(),
        )

    def toordinal(self):
        return (dateutil.parser.parse(self.day), self.start)
    
    def cost(self, task):
        c = 0
        diff_cost = 5
        for i, r in enumerate(task.wants()):
            if r in self.resource_order:
                rind = self.resource_order.index(r)
                diff = rind - i
                c += diff_cost * (diff if diff > 0 else 0) * 0.9**i
            else:
                c += diff_cost * len(task.wants())

        return c
        
    def can_complete(self, task):
        # also check against task needs list
        dateutil.parser.parse(self.day) <= task.due()
    
    def num_minutes(self):
        return self.end - self.start
        # fmt = ''
        # start = datetime.strptime(self.start, fmt)
        # end = datetime.strptime(self.end, fmt)
        # td = te - ts

        #return td.seconds // 60
    
class Scheduler:
    def __init__(self, tasktree, schedule_file):
        self._tasktree = tasktree
        self._datatree = utils.file_to_dict(schedule_file)

        abbrevs = [
            (['mon', 'm'], 'monday'),
            (['tues', 't'], 'tuesday'),
            (['wed', 'w'], 'wednesday'),
            (['thurs', 'r'], 'thursday'),
            (['fri', 'f'], 'friday'),
            (['sat', 's'], 'saturday'),
            (['sun', 'u'], 'sunday'),
        ]

        def extend_map(acc, abbrev_tup):
            abbrev, day = abbrev_tup
            acc.update(dict.fromkeys(abbrev, day))
            return acc

        self.abbrev_map = reduce(extend_map, abbrevs, {})

    def expand_day(self, day_abbrev):
        return self.abbrev_map[day_abbrev] if day_abbrev in self.abbrev_map else 'unknown'

    def time_blocks(self):
        def time_block_gen():
            for k, v in self._datatree.items():
                name = k
                if isinstance(v, list) and len(v) > 1:
                    base = v[0]
                    time_defs = [dict(base, **d) for d in v[1:]]
                elif isinstance(v, dict):
                    base = v
                    time_defs = [v]
                else:
                    print('Wtf are you putting in your schedule config?')
                    exit(1)

                for d in time_defs:
                    if 'days' in d:
                        for day in d['days']:
                            day = self.expand_day(day)
                            block = dict(base, name=k, start=d['start'], end=d['end'], day=day)
                            yield TimeBlock(block)

        return sorted(list(time_block_gen()), key = lambda b: b.toordinal());
                
    def scheduled_tasks(self):
        tasks = self._tasktree.leaves()
        time_blocks = self.time_blocks()
        total_minutes = 0
        graph = nx.DiGraph()

        for i, tb in enumerate(time_blocks):
            nm = tb.num_minutes()
            total_minutes += nm
            graph.add_node('time.{}'.format(i), demand=-nm)

        graph.add_node('sink', demand=total_minutes)
        graph.add_node('excess', demand=0)
        graph.add_edge('excess', 'sink')

        for j, task in enumerate(tasks):
            graph.add_node('task.{}'.format(j))
            graph.add_edge('task.{}'.format(j), 'sink')
            
        for i, tb in enumerate(time_blocks):
            graph.add_edge('time.{}'.format(i), 'excess', weight=1000)
            for j, task in enumerate(tasks):
                if tb.can_complete(task):
                    graph.add_edge(
                        'time.{}'.format(i),
                        'task.{}'.format(j),
                        weight=tb.cost(task),
                        capacity=task.time(),
                    )

        return nx.min_cost_flow(graph)
