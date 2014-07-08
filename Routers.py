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
        self.region_num = int()
        if gui_boolean:
            self.canvas_id = canvas_id
   
    def total_load(self):
        return len(self.incoming) 





class IPRouter:
# Name based content facilitated server

  def __init__(self, _id, canvas_id, gui_boolean):
    self.id = _id
    self.incoming = deque()
    self.responses = deque()
    self.color = ''
    self.forwarding_table = {}
    self.content_store = {}
    self.contained_regions = {}
    self.region_num = int()
    if gui_boolean:
        self.canvas_id = canvas_id
 
  def total_load(self):
    return len(self.incoming) 



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