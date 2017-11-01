import networkx as nx, dateutil.parser, re

from flextime import utils
from functools import reduce
from datetime import datetime

class TimeBlock:
    max_cost = 1000
    def __init__(self, data):
        required_keys = ['day', 'name', 'start', 'end', 'resource_order']
        if all([k in data for k in required_keys]):
            for k, v in data.items():
                setattr(self, k, v)
        else:
            print('Missing required attributes in TimeBlock')
            exit(1)

    def __str__(self):
        return "{} {}: {}-{}\n\t{}\n".format(
            self.day,
            self.name,
            '{:02d}:{:02d}'.format(*divmod(self.start, 60)),
            '{:02d}:{:02d}'.format(*divmod(self.end, 60)),
            "\n\t".join([str(t) for t in self.tasks]),
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

        return c if c <= TimeBlock.max_cost else TimeBlock.max_cost
        
    def can_complete(self, task):
        within_due = dateutil.parser.parse(self.day) <= task.due()
        needs_satisfied = all([(n in self.resource_order) for n in task.needs()])

        return within_due and needs_satisfied
    
    def num_minutes(self):
        return self.end - self.start
    
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
        time_blocks = self.time_blocks()
        graph = nx.DiGraph()

        total_minutes = 0
        total_task_minutes = 0
        unscheduled_tasks = []

        for i, tb in enumerate(time_blocks):
            total_minutes += tb.num_minutes()
            graph.add_node('time.{}'.format(i))

        tasks = self._tasktree.sorted_leaves('d')

        for j, task in enumerate(tasks):
            if total_task_minutes + task.time() <= total_minutes:
                total_task_minutes += task.time()
            else:
                unscheduled_tasks = tasks[j:]
                tasks = tasks[:j]
                break

        graph.add_node('source', demand=-total_task_minutes)

        for j, task in enumerate(tasks):
            graph.add_node('task.{}'.format(j), demand=task.time())
            graph.add_edge('source', 'task.{}'.format(j), weight=TimeBlock.max_cost + 1)


        for i, tb in enumerate(time_blocks):
            graph.add_edge('source', 'time.{}'.format(i), capacity=tb.num_minutes())
            for j, task in enumerate(tasks):
                if tb.can_complete(task):
                    graph.add_edge(
                        'time.{}'.format(i),
                        'task.{}'.format(j),
                        weight=tb.cost(task),
                    )

        try:
            flowDict = nx.min_cost_flow(graph)
        except nx.exception.NetworkXUnfeasible:
            print("No optimal solution found; you're probably going to lose some sleep.")
            exit(1)

        for i, tb in enumerate(time_blocks):
            time_key = 'time.{}'.format(i)
            tb.tasks = [task for j, task in enumerate(tasks) if 'task.{}'.format(j) in flowDict[time_key] and flowDict[time_key]['task.{}'.format(j)] > 0]

        unscheduled_tasks += [task for i, task in enumerate(tasks) if 'task.{}'.format(i) in flowDict['source'] and flowDict['source']['task.{}'.format(i)] > 0]
        
        return (unscheduled_tasks, time_blocks)