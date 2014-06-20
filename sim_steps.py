for n in reversed(range(1, len(Network.nodes))):
    #print 'node: ' + str(n) + ' processing'
    #logging.debug(' processing node %d ', n)
    Network.process(n)
Network.deliver_in_transit_packets()



execfile("build_and_publish_sim.py")



# BUILD NETWORK 
def build_the_network(levels):
	logging.debug(' Building network with %d levels ...' % levels)
	Network.build(levels,0)
	logging.debug(' Building Complete')
	logging.debug(' Node size is %d' % len(Network.nodes))

# PUBLISH CONTENT AND UPDATE FORWARDING TABLES
def publish_content(content_name, content_data, dest_id):
	logging.debug(' Publishing content: (%s)  to  node %d  content store...', content_name, dest_id)
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


def begin_initial_request(content_name, _id):
	# Run Simulation
	logging.debug(' Initializing Simulation ...')
	source_id = _id
	logging.debug(' Initializing request for %s at node %d', content_name, source_id)
	Network.nodes[source_id].incoming.append({'content_name': content_name, 'from_id':0, '_type': 'request' })  # 0 signifies that it is the source of request
	logging.debug('  Simulation ready: ')




