# To run this script from shell --> execfile("build_and_publish_sim.py")
import logging
import Network 

# 
logging.getLogger().setLevel(logging.DEBUG)




'''
levels = 3
logging.debug(' Building network with %d levels ...' % levels)
Network.build(levels,0)
logging.debug(' Building Complete')
logging.debug(' Node size is %d' % len(Network.nodes))
'''
# BUILD NETWORK 
def build_the_network(levels):
	if len(Network.nodes) > 0:
		Network.nodes.clear()
	logging.debug(' Building network with %d levels ...' % levels)
	Network.build(levels,0)
	logging.debug(' Building Complete')
	logging.debug(' Node size is %d' % len(Network.nodes))




'''
#
dest = 13
content_name = 'heat vs. spurs'
content_data = 'Spurs win Game 1'
logging.debug(' Publishing content: (%s)  to  node %d  content store...', content_name, dest)
Network.nodes[13].content_store[content_name] =  content_data
logging.debug(' Publishing Complete')

logging.debug(' Updating forwarding tables of parents of node %d ... ' % dest)
# Get all parents of dest node until reaching root 1
flag = False
current = 13
parent_id = Network.get_parent(dest)
while ( parent_id != 0 ):    # parent of 1 always returns 0
	Network.nodes[parent_id].forwarding_table[content_name] = current
	logging.debug(' Updated forwarding table of node %d ' % parent_id)
	logging.debug(' Forwarding table now is: %s', str(Network.nodes[parent_id].forwarding_table))
	current = parent_id
	parent_id = Network.get_parent(parent_id)


# Run Simulation
logging.debug(' Initializing Simulation ...')
source_id = 11
logging.debug(' Initializing request for %s at node %d', content_name, source_id)
Network.nodes[source_id].incoming.append({'content_name': content_name, 'from_id':0, '_type': 'request' })  # 0 signifies that it is the source of request
logging.debug('  Simulation ready: ')
'''
# PUBLISH CONTENT AND UPDATE FORWARDING TABLES
def publish_content(Network, content_name, content_data, dest_id):
	logging.debug(' Publishing content: (%s)  to  node %d', content_name, dest_id)
	Network.nodes[dest_id].content_store[content_name] =  content_data
	logging.debug(' Publishing Complete')


	logging.debug(' Updating forwarding tables of parents of node %d ... ' % dest_id)
	# Get all parents of dest node until reaching root 1
	flag = False
	current = dest_id
	parent_id = Network.get_parent(dest_id)
	while ( parent_id != 0 ):    # parent of 1 always returns 0
		Network.nodes[parent_id].forwarding_table[content_name] = current
		logging.debug(' Updated forwarding table of node %d ' % parent_id)
		logging.debug(' Forwarding table now is: %s', str(Network.nodes[parent_id].forwarding_table))
		current = parent_id
		parent_id = Network.get_parent(parent_id)
	logging.debug(' Completed updating FT of parents of %d ' % dest_id)


def begin_initial_request(content_name, _id):
	# Run Simulation
	logging.debug(' Initializing Simulation ...')
	source_id = _id
	logging.debug(' Initializing request for %s at node %d', content_name, source_id)
	Network.nodes[source_id].incoming.append({'content_name': content_name, 'from_id':0, '_type': 'request' })  # 0 signifies that it is the source of request
	logging.debug('  Simulation ready: ')




def step():
	for n in reversed(range(1, len(Network.nodes))):
		 Network.process(n)


def deliver():
	Network.deliver_in_transit_packets()


def summary(node_number):
	n = node_number
	print 'forwaring table: ' + str(Network.nodes[n].forwarding_table)
	print 'incoming queue: ' + str(Network.nodes[n].incoming)
	print 'content store: ' + str(Network.nodes[n].content_store)
	print 'pending table: ' + str(Network.nodes[n].pending_table)
	print 'incoming length: ' + str(len(Network.nodes[n].incoming))
	print 'incomming len >= 1? ' + str(len(Network.nodes[n].incoming) >=1)




