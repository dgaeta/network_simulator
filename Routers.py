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
    self.cache_max = 0
    self.cache_slots = []
    self.content_store = {}
    self.pending_table = {}
    self.local_tick_count = {}
    self.region_num = int()
    self.TDD_limit = 500
    self.max_resends = 5
    self.parent_id = self.get_parent(_id)
    if gui_boolean:
        self.canvas_id = canvas_id
 
  def total_load(self):
    return len(self.incoming) 

  def cache_content(self, content_name, content_data):
    if len(self.cache_slots) < self.cache_max:  # Cache slots
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

  def update_forwarding(self, content_name, forward_to_id):
    if content_name in self.forwarding_table:
      # Case 1: content pointer/data is not new to this router
      if not(forward_to_id in self.forwarding_table[content_name].forwarding_options):
        self.forwarding_table[content_name].forwarding_options.append(forward_to_id)
    else:
      self.forwarding_table[content_name] = ForwardingTable_Entry(content_name,forward_to_id)

  def check_TTD(self, network):
    for content_name in self.pending_table:
      entry = self.pending_table[content_name]
      if entry.current_TDD > self.TDD_limit:
        if entry.send_attempts < self.max_resends:
          network.prepare_packet('request', entry.content_name, self.id, entry.forwarded_to_id, 0, {'is_copy':True} )
          entry.send_attempts += 1
          entry.current_TDD = 0 # reset the current TDD
        else:
          self.reverse_publish(entry.content_name, entry.forwarded_to_id, network)
          if entry.content_name in self.forwarding_table:
            entry.sent_to_id = self.get_forward_to(entry.content_name)
            entry.current_TDD = 0 
            entry.send_attempts = 1
            network.prepare_packet('request', entry.content_name, self.id, self.get_forward_to(entry.content_name), 0)
          else: 
            network.prepare_packet('request', packet.content_name,packet.from_id,self.parent_id, 0, {'is_searching_for_new_route':True})
            del self.pending_table[entry.content_name]
          

  def get_forward_to(self,content_name):
    min_id = self.forwarding_table[content_name].best_option
    self.forwarding_table[content_name].historical_ticks[min_id] = 1
    return min_id

  def update_forwarding_history(self,content_name, sent_to_id, ticks):
    print self.id
    self.forwarding_table[content_name].historical_ticks[sent_to_id] = ticks
    self.update_forward_best_option(content_name)

  def update_forward_best_option(self,content_name):
    min_id = self.forwarding_table[content_name].forwarding_options[0]
    min_ticks = self.forwarding_table[content_name].historical_ticks[min_id]
    for key in self.forwarding_table[content_name].historical_ticks:
      value = self.forwarding_table[content_name].historical_ticks[key]
      if value < min_ticks:
        min_id = key
        min_ticks = value
    self.best_option = min_id
    

  ## ** TODO - refactor this and make it O(1) using dictionaries in forwarding table
  ## ** ^^ i.e. refactor how forwarding table work
  def reverse_publish(self,content_name,forwarded_to_id,network):
    current_id = self.id
    forward_to_id = forwarded_to_id
    while ( current_id != -1 ):    # update the forwarding to 
      network.nodes[current_id].remove_forward(content_name,forward_to_id)
      forward_to_id = current_id
      current_id = self.get_parent(current_id)


  def remove_forward(content_name,forward_to_id):
    if forward_to_id in self.forwarding_table[content_name]:
        self.forwarding_table[content_name].remove(forward_to_id)
        if not self.forwarding_table[content_name]:
          del self.forwarding_table[content_name]

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



class PendingTable_Entry(object):
  """docstring for PendingTable_Entry"""
  def __init__(self, content_name, life_ticks, sent_to_id, packet):
    self.content_name = content_name
    self.forwarded_to_id = sent_to_id
    self.life_ticks = life_ticks
    self.current_TDD = 0
    self.received_packets = [packet]
    self.send_attempts = 1
    self.requesters = [packet.origin_id]

class ForwardingTable_Entry(object):
  """docstring for PendingTable_Entry"""
  def __init__(self, content_name, forwarding_option):
    self.content_name = content_name
    self.forwarding_options = [forwarding_option]
    self.historical_ticks = {forwarding_option:0}
    self.best_option = forwarding_option



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
    self.local_tick_count = {}
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