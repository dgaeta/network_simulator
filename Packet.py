##
# Packet 
# 
# Name Based Routing Designed by: Armand Prieditis 
##

import logging
import time
logging.getLogger().setLevel(logging.DEBUG)

class Packet(object):
	"""docstring for Packet"""
	def __init__(self, _type, content_name, origin_id, dest_id,  *args):
		super(Packet, self).__init__()
		self.content_name = content_name
	 	self.origin_id = origin_id   
	 	if args:         				
	 		self.content_data =  args[0]
	 	else:
	 		self.content_data = 'None'				
	  	self.type = _type	
	  	self.dest_id = dest_id
	  	self.ticks= 0 
	  

	def __str__(self):
		return "type: " + self.type + " -- content_name: " + str(self.content_name) + " -- origin_id: " + str(self.origin_id) + " -- dest_id: " + str(self.dest_id) + " -- ticks: " + str(self.ticks) + " -- content_data: " + str(self.content_data)
