##
# Name Based Router and IP Router
# 
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
    self.cache_slots = []
    self.content_store = {}
    self.pending_table = {}
    self.region_num = int()
    if gui_boolean:
        self.canvas_id = canvas_id
 
  def total_load(self):
    return len(self.incoming) 

  def cache_content(self, content_name, content_data):
    if len(self.cache_slots) < 20:  # Cache slots
      self.cache_slots.append(content_name)
      self.content_store[content_name] = content_data
    else:
      popped = self.cache_slots.pop()
      del self.content_store[popped]
      self.cache_slots.append(content_name)
      self.content_store[content_name] = content_data

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
    self.cache_slots = []
    self.contained_regions = {}
    self.region_num = int()
    if gui_boolean:
        self.canvas_id = canvas_id
 
  def total_load(self):
    return len(self.incoming) 


  def cache_content(self, content_name, content_data):
    if len(self.cache_slots)< 20:  # Cache slots
      self.cache_slots.append(content_name)
      self.content_store[content_name] = content_data
    else:
      popped = self.cache_slots.pop()
      del self.content_store[popped]
      self.cache_slots.append(content_name)
      self.content_store[content_name] = content_data


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