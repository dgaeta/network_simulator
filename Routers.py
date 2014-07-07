##
# Name Based Router
# 
#
# author: Daniel Gaeta 
# Name Based Routing Designed by: Armand Prieditis 
##

from collections import deque
import logging
logging.getLogger().setLevel(logging.DEBUG)

from Packet import *

class NBRouter:
# Name based content facilitated server

    def __init__(self, _id, canvas_id, gui_boolean):
        self.id = _id
        self.incoming = deque()
        self.responses = deque()
        self.color = ''
        self.forwarding_table = {}
        self.content_store = {}
        self.pending_table = {}
        if gui_boolean:
            self.canvas_id = canvas_id
   
    def total_load(self):
        return len(self.incoming) 


    def incoming_packet(self, content_name, from_id, _type):
        # if requester_id == 1, it is the source of request
        self.incoming.append({'content_name': content_name,  'from_id': from_id, 'type': _type})
        logging.debug(' Request received from %d, enqueueing at %d, request for: %s', from_id, self.id, content_name) 
        self.req_load += 1

         
    def outgoing_packet( self, packet, in_transit_packets):
        print "GOT TO OUTGOING"
        # Valid args: Network.deliver_in_transit_packets(), content_name, content_data, dest_id, _type
        if packet['_type'] == 'request':
          # Case 1: forwarding a request
          logging.debug(' Forwarding a request for  %s, from %d to %d', packet['content_name'], packet['from_id'], packet['dest_id']) 
          in_transit_packets.append(packet)
        elif packet['_type'] == 'response':
          # Case 2: forwarding a response
          in_transit_packets.append(packet)
          #self.res_load += 1
        else: 
          logging.warning(' no type given for outgoing packet')



class IPRouter:
# Name based content facilitated server

    def __init__(self, _id, canvas_id, gui_boolean):
        self.id = _id
        self.incoming = deque()
        self.responses = deque()
        self.color = ''
        self.forwarding_table = {}
        self.content_store = {}
        if gui_boolean:
            self.canvas_id = canvas_id
   
    def total_load(self):
        return len(self.incoming) 


    def incoming_packet(self, content_name, from_id, _type):
        # if requester_id == 1, it is the source of request
        self.incoming.append({'content_name': content_name,  'from_id': from_id, 'type': _type})
        logging.debug(' Request received from %d, enqueueing at %d, request for: %s', from_id, self.id, content_name) 
        self.req_load += 1

         
    def outgoing_packet( self, packet, in_transit_packets):
        print "GOT TO OUTGOING"
        # Valid args: Network.deliver_in_transit_packets(), content_name, content_data, dest_id, _type
        if packet['_type'] == 'request':
          # Case 1: forwarding a request
          logging.debug(' Forwarding a request for  %s, from %d to %d', packet['content_name'], packet['from_id'], packet['dest_id']) 
          in_transit_packets.append(packet)
        elif packet['_type'] == 'response':
          # Case 2: forwarding a response
          in_transit_packets.append(packet)
          #self.res_load += 1
        else: 
          logging.warning(' no type given for outgoing packet')

    def get_parent(self, node_id):   
      n = node_id
      if n == 0: 
        return -1
      if (n <= 7):
        return 0 
      elif (n%7 == 1):
        return (n/7)
      else:
        return self.get_parent((n - ((n-1)%7))) #need one more level up because it was not a center node

    def forwarding(self,target_id):
      forward_to = target_id
      while self.get_parent(forward_to) > self.id:
        forward_to = self.get_parent(forward_to)
      return forward_to



##
# End of Program
##