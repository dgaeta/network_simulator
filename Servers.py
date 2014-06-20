from collections import deque
import logging
logging.getLogger().setLevel(logging.DEBUG)

class NBServer:
# Name based content facilitated server

  def __init__(self, _id, canvas_id):
    self.id = _id
    self.canvas_id = canvas_id
    self.incoming = deque()
    self.responses = deque()
    self.req_load = 0 
    self.res_load = 0
    self.total_load = 0
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

         
  def outgoing_packet( self, args, in_transit_packets):
    # Valid args: Network.deliver_in_transit_packets(), content_name, content_data, dest_id, _type
    if args['_type'] == 'request':
      # Case 1: forwarding a request
      logging.debug(' Forwarding a request for  %s, from %d to %d', args['content_name'], args['from_id'], args['dest_id']) 
      in_transit_packets.append({'content_name': args['content_name'],  'from_id': args['from_id'] , '_type':'request', 'dest_id': args['dest_id'], 'size':args['size']})
    elif args['_type'] == 'response':
      # Case 2: forwarding a response
      in_transit_packets.append({'content_name': args['content_name'] , 'from_id': args['from_id'], 'content_data': args['content_data'], '_type':'response','dest_id': args['dest_id'], 'size':args['size']})
      #self.res_load += 1
    else: 
      logging.warning(' no type given for outgoing packet')

          
  def color(self):
    pass
