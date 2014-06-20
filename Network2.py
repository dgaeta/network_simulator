import math 
import logging
from time import sleep
from collections import deque
from Tkinter import *

# Output debug level logs
logging.getLogger().setLevel(logging.DEBUG)

# DS 
global events, nodes
nodes = {}
in_transit_packets = []


def Network():
  def __init__(self, levels):
    self.root = tk.Tk()
    self.canvas = Canvas( self.root, width=400, height=400)
    self.nodes = {}
    self.in_transit_packets = []

    build(levels)
    self.canvas.pack(fill=BOTH, expand=1)   
    self.canvas.update()
    self.root.mainloop()

  # Defines and processes a single event per node / per unit of time
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


  # Seperates internal node processing from messages
  def deliver_in_transit_packets():
    while( len(in_transit_packets) > 0):
      packet = in_transit_packets.pop()
      dest_id = packet['dest_id']
      nodes[dest_id].incoming.append(packet) 
      logging.debug(" Delivered packet from %d to %d", packet['from_id'], packet['dest_id'])


  # Generates the network hierarchy: includes NBServer's in 'nodes' dictionary and Tkinter canvas widgets
  def build(levels):
    build(levels, 0, 30, 0, 0 )

  # build helper function
  def _build(level,i,r,x,y):
    #center = 7i+1
    #north = 7i+2
    #south = 7i+3
    #northaast = 7i+4
    #southeast = 7i+5
    #northwest = 7i+6
    #southwest = 7i+7
    
      
    if level > 0:

      #center
      self.nodes[7*i+1] = self.canvas.create_circle(x, y , r, outline = 'grey', width = 2.0)
      build(level-1,7*i+1,r/3,x,y)

      #north
      self.nodes[7*i+2] = self.canvas.create_circle(x, y , r, outline = 'grey', width = 2.0)
      build(level-1,7*i+2,r/3,x,y+(2.0*r))

      #south
      self.nodes[7*i+3] = self.canvas.create_circle(x, y , r, outline = 'grey', width = 2.0)
      build(level-1,7*i+3,r/3,x,y-(2.0*r))

      #northeast
      self.nodes[7*i+4] = self.canvas.create_circle(x, y , r, outline = 'grey', width = 2.0)
      build(level-1,7*i+4,r/3,x+2*r*math.sqrt(3)/2,y+r)

      #southeast
      self.nodes[7*i+5] = self.canvas.create_circle(x, y , r, outline = 'grey', width = 2.0)
      build(level-1,7*i+5,r/3,x+2*r*math.sqrt(3)/2,y-r)

      #northwest
      self.nodes[7*i+6] = self.canvas.create_circle(x, y , r, outline = 'grey', width = 2.0)
      build(level-1,7*i+6,r/3,x-2*r*math.sqrt(3)/2,y+r)

      #southwest
      self.nodes[7*i+7] = self.canvas.create_circle(x, y , r, outline = 'grey', width = 2.0)
      build(level-1,7*i+7,r/3,x-2*r*math.sqrt(3)/2,y-r)

    else:
      if level == 0:
        #center
        self.nodes[7*i+1] = self.canvas.create_circle(x, y , r, outline = 'grey', width = 2.0)

        #north
        self.nodes[7*i+2] = self.canvas.create_circle(x, y , r, outline = 'grey', width = 2.0)

        #south
        self.nodes[7*i+3] = self.canvas.create_circle(x, y , r, outline = 'grey', width = 2.0)

        #northeast
        self.nodes[7*i+4] = self.canvas.create_circle(x, y , r, outline = 'grey', width = 2.0)

        #southeast
        self.nodes[7*i+5] = self.canvas.create_circle(x, y , r, outline = 'grey', width = 2.0)

        #northwest
        self.nodes[7*i+6] = self.canvas.create_circle(x, y , r, outline = 'grey', width = 2.0)

        #southwest
        self.nodes[7*i+7] = self.canvas.create_circle(x, y , r, outline = 'grey', width = 2.0)

   

  # 
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


  # 
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


  # Represents a single process for each node in the network in a single unit of time, then delivers packets in transit
  def step(size =len(nodes)):
      for n in reversed(range(1, size)):
          #print 'node: ' + str(n) + ' processing'
          #logging.debug(' processing node %d ', n)
          process(n)
      deliver_in_transit_packets()

        
