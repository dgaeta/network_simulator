##
# Packet 
# 
# Name Based Routing Designed by: Armand Prieditis 
##

import logging
import time
import uuid
logging.getLogger().setLevel(logging.DEBUG)

class Packet(object):
	"""docstring for Packet"""
	def __init__(self, id, _type, content_name, origin_id, dest_id, **kwargs):
		super(Packet, self).__init__()
		if id == 0:
			self.id = str(uuid.uuid4())
		else:
			self.id = id
		self.content_name = content_name
	 	self.origin_id = origin_id   
	 	if 'content_data' in kwargs:         				
	 		self.content_data =  kwargs['content_data']
	 	else:
	 		self.content_data = 'None'				
	  	self.type = _type	
	  	self.dest_id = dest_id
	  	self.ticks= 0 
	  	self.is_copy = False
	  	self.send_attempts = 1
	  	self.current_TTD = 0
	  	if 'no_content_exists' in kwargs:
	  		self.no_content_exists = True
	  	else: 
	  		self.no_content_exists = False

	  	if 'is_searching_for_new_route' in kwargs:
	  		self.is_searching_for_new_route = True
	  	else:
	  		self.is_searching_for_new_route = False
	  

	def __str__(self):
		return "type: " + self.type + " -- content_name: " + str(self.content_name) + " -- origin_id: " + str(self.origin_id) + " -- dest_id: " + str(self.dest_id) + " -- ticks: " + str(self.ticks) + " -- content_data: " + str(self.content_data)
