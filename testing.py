#import networkx as nx

# G = nx.DiGraph()
# G.add_node('CCIT', demand=-180)
# G.add_node('CSCI442p1', demand=0)
# G.add_node('CSCI442p2', demand=0)
# G.add_node('Excess', demand=0)
# G.add_node('Sink', demand=180)

# G.add_edge('CCIT', 'CSCI442p1', weight=3, capacity=30)
# G.add_edge('CCIT', 'CSCI442p2', weight=3, capacity=30)
# G.add_edge('CCIT', 'Excess', weight=5)

# G.add_edge('CSCI442p1', 'Sink')
# G.add_edge('CSCI442p2', 'Sink')
# G.add_edge('Excess', 'Sink')

# flowDict = nx.min_cost_flow(G)
# print(flowDict)

from flextime import Scheduler, TaskTree, utils

s = Scheduler(TaskTree(), 'schedule.yml')

for t in s.scheduled_tasks():
    print(str(t))

#print(utils.dump_dict(s.scheduled_tasks()))
# tbs = s.time_blocks()
#print(utils.dump_dict(s.time_blocks()))
