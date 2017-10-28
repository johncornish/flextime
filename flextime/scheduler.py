import networkx as nx, dateutil.parser

from flextime import utils
from functools import reduce
from datetime import datetime

class TimeBlock:
    def __init__(self, data):
        self._data = data

    def num_minutes(self):
        if all(k in self._data for k in ['start', 'end']):
            start = datetime.strptime(self._data['start'], fmt)
            end = datetime.strptime(self._data['end'], fmt)
            td = te - ts

            return td.seconds // 60
    
class Scheduler:
    def __init__(self, tasktree, schedule_file):
        self._days = [
            'monday',
            'tuesday',
            'wednesday',
            'thursday',
            'friday',
            'saturday',
            'sunday',
            'unknown',
        ]
        self._tasktree = tasktree
        self._datatree = utils.file_to_dict(schedule_file)
        self.build_graph()

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
        day_map = dict.fromkeys(self._days, [])

        for k, v in self._datatree.items():
            name = k
            if isinstance(v, list) and len(v) > 1:
                base = v[0]
                time_defs = [dict(base, **d) for d in v[1:]]
            elif isinstance(v, dict):
                time_defs = [v]
            else:
                print('Wtf are you putting in your schedule config?')
                exit(1)

            for d in time_defs:
                if 'days' in d:
                    for day in d['days']:
                        day = self.expand_day(day)
                        block = dict(base, start=d['start'], end=d['end'], day=day)
                        day_map[day].append(TimeBlock(block))

        return reduce(lambda acc, d: acc + day_map.get(d), self._days, [])
                
    def build_graph(self):
        #tasks = self._tasktree.leaves()
        #time_blocks = self.time_blocks()
        pass
