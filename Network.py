import math 
import logging
import time 
from collections import deque
logging.getLogger().setLevel(logging.DEBUG)

global events, nodes
nodes = {}
events = []
in_transit_packets = []

class NBServer:
# Name based content facilitated server

    def __init__(self, _id):
        self.id = _id
        self.incoming = deque()
        self.responses = deque()
        self.req_load = 0 
        self.res_load = 0
        self.color = ''
        self.forwarding_table = {}
        self.content_store = {}
        self.pending_table = {}

    def __str__(self):
        string = 'current load: ' + str(self.req_load + self.res_load) 
        return string

    
    def incoming_packet(self, content_name, from_id, _type):
        # if requester_id == 1, it is the source of request
        self.incoming.append({'content_name': content_name,  'from_id': from_id, 'type': _type})
        logging.debug(' Request received from %d, enqueueing at %d, request for: %s', from_id, self.id, content_name) 
        self.req_load += 1
    
           
    def outgoing_packet( self, args):
        # Valid args: Network.deliver_in_transit_packets(), content_name, content_data, dest_id, _type
        if args['_type'] == 'request':
            # Case 1: forwarding a request
            logging.debug(' Forwarding a request for  %s, from %d to %d', args['content_name'], args['from_id'], args['dest_id']) 
            in_transit_packets.append({'content_name': args['content_name'],  'from_id': args['from_id'] , '_type':'request', 'dest_id': args['dest_id']})
        elif args['_type'] == 'response':
            # Case 2: forwarding a response
            in_transit_packets.append({'content_name': args['content_name'] , 'from_id': args['from_id'], 'content_data': args['content_data'], '_type':'response','dest_id': args['dest_id']})
            self.res_load += 1
        else: 
            logging.warning(' no type given for outgoing packet')
    
            
    def color(self):
        pass



def process(node_id):
        logging.debug(' processing incoming packet at %d' % node_id)
        if len(nodes[node_id].incoming) >= 1:
            logging.debug(' processing incoming packet at %d' % node_id)
            packet = nodes[node_id].incoming.popleft()
            pack = str(packet)
            logging.debug(" packet data: %s", pack) 
                   
            if packet['_type'] == 'request':
                # Packet is a request      
                content_name = packet['content_name']
                requester_id = packet['from_id']    

                # Case 1: content in cache
                if content_name in nodes[node_id].content_store:    
                    nodes[node_id].outgoing_packet({ 'content_name': content_name, 'from_id':node_id, 'content_data':nodes[node_id].content_store[content_name],  'dest_id':requester_id, '_type':'response'})
                    logging.debug(" content %s already in cache", content_name) 
                    logging.debug(" sent content back to  %d ", requester_id)
                    
                # Case 2: duplicate request exists
                elif content_name in nodes[node_id].pending_table:   
                    nodes[node_id].pending_table[content_name] + [requester_id]
                    logging.debug(" duplicate request for content %s , added requester_id %d to PT", packet[content_name], packet[requester_id]) 
            
                # Case 3: no pending request, but location lives in children, create entry in PT, send request to child
                elif content_name in nodes[node_id].forwarding_table:
                    directed_child_id  = nodes[node_id].forwarding_table[content_name]   #direction of child where destination node is contained 
                    nodes[node_id].pending_table[content_name] = [requester_id]          # entry in PT created
                    nodes[node_id].outgoing_packet( {'content_name': content_name , 'dest_id':directed_child_id, 'from_id': node_id, '_type': 'request'})
                    logging.debug(" location content %s known, entry for requester %d created in PT", content_name, requester_id) 
                    logging.debug(" forwarded request to child %d ", directed_child_id )
                    
                # Case 4: no duplicate, add to PT, forward to parent 
                else: 
                    nodes[node_id].pending_table[content_name] = [requester_id]
                    parent_id = get_parent(node_id)
                    nodes[node_id].outgoing_packet({'content_name':content_name, 'from_id':node_id, 'dest_id': parent_id, "_type": 'request'})
                    logging.debug(" content %s NOT known, entry for requester %d created in PT, sent request to parent %d", content_name, requester_id, parent_id) 


            elif packet['_type'] == 'response':
                # packet is a response
                content_name = packet['content_name']
                data = packet['content_data']    

                # Case 1: node is source of request, 0 signifies it is the source of request
                if nodes[node_id].pending_table[content_name][0] ==  0:   
                    logging.debug(" DONE! I am the source: %d" % node_id)
                    nodes[node_id].content_store[content_name] = data
                    logging.debug(" Added content (%s) to content store"  % content_name)
                    del nodes[node_id].pending_table[content_name]
                    logging.debug(" Deleted content (%s) from PT"  % content_name)
                # Case 2: node was a middle man
                else:
                    print logging.debug("Forwarding response along to all requesters, I am: %d ... ", node_id)
                    for dest_id in nodes[node_id].pending_table[content_name]:
                        nodes[node_id].outgoing_packet({'content_name':packet['content_name'], 'from_id':node_id, 'content_data':data, '_type':'response', 'dest_id':dest_id} )
                        logging.debug("Sent response to requester %d ", dest_id)
                    logging.debug("Forwarding to all requesters complete")

                    del nodes[node_id].pending_table[packet['content_name']]
                    logging.debug(" Deleted content (%s) from PT"  % content_name)
                    nodes[node_id].content_store[packet['content_name']] = data
                    logging.debug(" Added content (%s) to content store"  % content_name)

            else:
                logging.warning(' Mislabeled Packet')


def deliver_in_transit_packets():
    while( len(in_transit_packets) > 0):
        packet = in_transit_packets.pop()
        dest_id = packet['dest_id']
        nodes[dest_id].incoming.append(packet) 
        logging.debug(" Delivered packet from %d to %d", packet['from_id'], packet['dest_id'])

def build(level,i):
    
    #center = 7i+1
    #north = 7i+2
    #south = 7i+3
    #northaast = 7i+4
    #southeast = 7i+5
    #northwest = 7i+6
    #southwest = 7i+7


    if level > 0:

        #center
        nodes.setdefault(7*i+1,NBServer(7*i+1))
        build(level-1, 7*i+1)

        #north
        nodes[7*i+2] = NBServer(7*i+1)
        build(level-1, 7*i+2)

        #south
        nodes[7*i+3] = NBServer(7*i+1)
        build(level-1, 7*i+3)

        #northeast
        nodes[7*i+4] = NBServer(7*i+1)
        build(level-1, 7*i+4)

        #southeast
        nodes[7*i+5] = NBServer(7*i+1)
        build(level-1, 7*i+5)

        #northwest
        nodes[7*i+6] = NBServer(7*i+1)
        build(level-1, 7*i+6)

        #southwest
        nodes[7*i+7] = NBServer(7*i+1)
        build(level-1, 7*i+7)

    elif level == 0:
        #center
        nodes[7*i+1] = NBServer(7*i+1)

        #north
        nodes[7*i+2] = NBServer(7*i+2)

        #south
        nodes[7*i+3] = NBServer(7*i+3)

        #northeast
        nodes[7*i+4] = NBServer(7*i+4)

        #southeast
        nodes[7*i+5] = NBServer(7*i+5)

        #northwest
        nodes[7*i+6] = NBServer(7*i+6)

        #southwest
        nodes[7*i+7] = NBServer(7*i+7)

def get_parent(node_id):
        n = node_id
        if n == 1: 
            return 0

        if (n <= 7):
            return 1 
        elif (n%7 == 1):
            return (n/7) 
        else:
            return (n - ((n-1)%7)) 

def get_child_at(dir, node_id):
    if (dir.lower() == 'c'):
        return 7*node_id + 1
    elif (dir.lower() == 'n'):
        return 7*node_id + 2
    elif (dir.lower() == 's'):
        return 7*node_id + 3
    elif (dir.lower() == 'ne'):
        return 7*node_id+ 4
    elif (dir.lower() == 'se'):
        return 7*node_id + 5
    elif (dir.lower() == 'nw'):
        return 7*node_id + 6
    elif (dir.lower() == 'sw'):
        return 7*node_id + 7
    else:
        return 'error'


def step(size =len(nodes)):
    for n in reversed(range(1, size)):
        #print 'node: ' + str(n) + ' processing'
        #logging.debug(' processing node %d ', n)
        process(n)
    deliver_in_transit_packets()

        
