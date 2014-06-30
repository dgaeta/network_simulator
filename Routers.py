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

class NBRouter:
# Name based content facilitated server

  def __init__(self, _id, canvas_id):
    self.id = _id
    self.canvas_id = canvas_id
    self.incoming = deque()
    self.responses = deque()
    self.color = ''
    self.forwarding_table = {}
    self.content_store = {}
    self.pending_table = {}
   
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
      print 'outgoing_packet time_start is ' + str( packet['time_start'])
      in_transit_packets.append(packet)
    elif packet['_type'] == 'response':
      # Case 2: forwarding a response
      in_transit_packets.append(packet)
      #self.res_load += 1
    else: 
      logging.warning(' no type given for outgoing packet')

          
  def color(self):
    pass


##
# End of Program
##