import logging
import Simulation as sim

# 
logging.getLogger().setLevel(logging.DEBUG)

if len(sim.nodes) > 0:
	sim.nodes.clear()

#
levels = 3
logging.debug(' Building network with %d levels ...' % levels)
sim.build(levels,0)
logging.debug(' Building Complete')
logging.debug(' Node size is %d' % len(sim.nodes))

#
dest = 13
content_name = 'heat vs. spurs'
content_data = 'Spurs win Game 1'
logging.debug(' Publishing content: (%s)  to  node %d  content store...', content_name, dest)
sim.nodes[13].content_store[content_name] =  content_data
logging.debug(' Publishing Complete')

logging.debug(' Updating forwarding tables of parents of node %d ... ' % dest)
# Get all parents of dest node until reaching root 1
flag = False
parent_id = sim.get_parent(dest)
while ( parent_id != 0 ):    # parent of 1 always returns 0
	sim.nodes[parent_id].forwarding_table[content_name] = dest
	logging.debug(' Updated forwarding table of node %d ' % parent_id)
	parent_id = sim.get_parent(parent_id)


# Run Simulation
logging.debug(' Initializing Simulation ...')
source_id = 11
logging.debug(' Initializing request for %s at node %d', content_name, source_id)
sim.nodes[source_id].incoming.append({'content_name': content_name, 'from_id':0, '_type': 'request' })  # 0 signifies that it is the source of request
logging.debug('  Simulation ready: ')
