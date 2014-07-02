##
# Packet 
# 
#
# author: Daniel Gaeta 
# Name Based Routing Designed by: Armand Prieditis 
##

import logging
import time
logging.getLogger().setLevel(logging.DEBUG)

class Packet(object):
	"""docstring for Packet"""
	def __init__(self, _type, content_name, requester_id, dest_id,  *args):
		super(Packet, self).__init__()
		self.content_name = content_name
	 	self.requester_id = requester_id   
	 	if args:         				
	 		self.content_data =  args[0]
	 	else:
	 		self.content_data = 'None'				
	  	self.type = _type	
	  	self.dest_id = dest_id
	  	self.lifetime= 10 #represent milliseconds, 10 ms for packetization

	def __str__(self):
		return "type: " + self.type + " -- content_name: " + self.content_name + " -- requester_id: " + str(self.requester_id) + " -- dest_id: " + str(self.dest_id) + " -- lifetime: " + str(self.lifetime) + " -- content_data: " + self.content_data
