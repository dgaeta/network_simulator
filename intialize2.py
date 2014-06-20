# To run this script from shell --> execfile("intialize2.py")
import logging
import Network2

# 
logging.getLogger().setLevel(logging.DEBUG)

# BUILD NETWORK 
def build_the_network(levels):
  self.root = Tk()
  self.canvas = Canvas(self.root, width=400, height=400)
  
  if len(Network2.nodes) > 0:
    Network2.nodes.clear()
  logging.debug(' Building network with %d levels ...' % levels)
  Network2.build(levels,0)
  logging.debug(' Building Complete')
  logging.debug(' Node size is %d' % len(Network2.nodes))



# PUBLISH CONTENT AND UPDATE FORWARDING TABLES
def publish_content(content_name, content_data, dest_id):
  logging.debug(' Publishing content: (%s)  to  node %d', content_name, dest_id)
  Network2.nodes[dest_id].content_store[content_name] =  content_data
  logging.debug(' Publishing Complete')


  logging.debug(' Updating forwarding tables of parents of node %d ... ' % dest_id)
  # Get all parents of dest node until reaching root 1
  flag = False
  current = dest_id
  parent_id = Network2.get_parent(dest_id)
  while ( parent_id != 0 ):    # parent of 1 always returns 0
    Network2.nodes[parent_id].forwarding_table[content_name] = current
    logging.debug(' Updated forwarding table of node %d ' % parent_id)
    logging.debug(' Forwarding table now is: %s', str(Network2.nodes[parent_id].forwarding_table))
    current = parent_id
    parent_id = Network2.get_parent(parent_id)
  logging.debug(' Completed updating FT of parents of %d ' % dest_id)


def begin_initial_request(content_name, _id):
  # Run Simulation
  logging.debug(' Initializing Simulation ...')
  source_id = _id
  logging.debug(' Initializing request for %s at node %d', content_name, source_id)
  Network2.nodes[source_id].incoming.append({'content_name': content_name, 'from_id':0, '_type': 'request' })  # 0 signifies that it is the source of request
  logging.debug('  Simulation ready: ')




def step():
  for n in reversed(range(1, len(Network2.nodes))):
     Network2.process(n)


def deliver():
  Network2.deliver_in_transit_packets()


def summary(node_number):
  n = node_number
  print 'forwaring table: ' + str(Network2.nodes[n].forwarding_table)
  print 'incoming queue: ' + str(Network2.nodes[n].incoming)
  print 'content store: ' + str(Network2.nodes[n].content_store)
  print 'pending table: ' + str(Network2.nodes[n].pending_table)
  print 'incoming length: ' + str(len(Network2.nodes[n].incoming))
  print 'incomming len >= 1? ' + str(len(Network2.nodes[n].incoming) >=1)




