import Tkinter as tk
from time import sleep
import math
import logging
import Servers 
import random
import sys

logging.getLogger().setLevel(logging.DEBUG)

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler

def _create_circle(self, x, y, r, **kwargs):
	"""implementation for creating a circle in Tk"""
	return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
tk.Canvas.create_circle = _create_circle

def is_empty( any_structure):
		if any_structure:
			#print('Structure is not empty.')
			return False
		else:
			#print('Structure is empty.')
			return True

class AutoScrollbar(tk.Scrollbar):
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        tk.Scrollbar.set(self, lo, hi)
    def pack(self, **kw):
        raise TclError, "cannot use pack with this widget"
    def place(self, **kw):
        raise TclError, "cannot use place with this widget"

class Network(object):
	def __init__(self, levels, master):
		
		#### data structs for the network
		self.nodes = {}
		self.in_transit_packets = []
		self.levels = levels
		#self.lower_lim = 7**levels
		self.lower_lim = 400
		self.upper_lim = ((7**(levels+1))-3)
		self.active_requests = {}
		self.content_names = []
		self.flag = True
		self.delay = 500
		self.ammo = 0 
		self.button_pressed = tk.StringVar()
		self.button_pressed.set("To Start, Click 'Publish Content'")
		self.regions = []
		self.entry_value = tk.StringVar()
		####
		
		
		#### GUI for network sim 
		self.root = master


		vscrollbar = AutoScrollbar(self.root)
		vscrollbar.grid(row=0, column=1, sticky='n'+'s')
		hscrollbar = AutoScrollbar(self.root, orient='horizontal')
		hscrollbar.grid(row=1, column=0, sticky='e'+'w')

		#self.toolbar = tk.Frame(self.root)
		#self.toolbar.pack()

		self.canvas = tk.Canvas(self.root,
                yscrollcommand=vscrollbar.set,
                xscrollcommand=hscrollbar.set)
		self.canvas.grid(row=0, column=0, sticky='n'+'s'+'e'+'w')

		vscrollbar.config(command=self.canvas.yview)
		hscrollbar.config(command=self.canvas.xview)

		# make the canvas expandable
		self.root.grid_rowconfigure(0, weight=1)
		self.root.grid_columnconfigure(0, weight=1)


		#
		# create canvas contents
		self.frame = tk.Frame(self.canvas)
		self.frame.rowconfigure(1, weight=1)
		self.frame.columnconfigure(1, weight=1)

		
		# Photo for heatmap
		photo = tk.PhotoImage(file="heat1.gif")
		self.label = tk.Label(self.frame, text="Machine Load", image=photo, anchor='w', justify='left', compound=tk.BOTTOM)
		self.label.photo = photo
		self.label.pack(side='left')
		####		
		
		self.delay_scale = tk.Scale(self.frame, from_=0, to=5, orient='horizontal', command=self.update_delay, label='Sim Delay',
			)
		self.delay_scale.set(0)
		self.delay_scale.pack(side='left')

		self.request_freq = tk.Scale(self.frame, from_=0, to=100, orient='horizontal', command=self.reload, label='Request Freq Per Node', length=200
			)
		self.request_freq.set(0)
		self.request_freq.pack(side='left')
		
		#### Enqueue the build into the mainloop
		self.root.after(0, self.build(levels))
		self.root.after_idle(self.assemble_regions)



		####	
		#### Create a button to close the program

		
		
		# Create a button to publish the data
		#self.button = tk.Button(
		#	self.frame, text="Publish", fg="red", command=lambda: self.publish_content('ok','ok',686)
		#	)
		#self.button.pack(side='left')
		
		# Button for testing numbers
		#self.button = tk.Button(
		 #   self.frame, text="test num", fg="red", command=lambda: self.test_nums()
		  #  )
		#self.button.pack(side='left')
		
		# Button for intiating request
		#self.button = tk.Button(
		#	self.frame, text="Make Request", fg="red", command=lambda: self.begin_initial_request('ok', 444)
		#	)
		#self.button.pack(side='left')
		
		# Button for stepping through simulation
		#self.button = tk.Button(
		#	self.frame, text="Process", fg="red", command=lambda: self.step()
		#	)
		#self.button.pack(side='left')
		
		#
		#self.button = tk.Button(
		#	self.frame, text="Deliver", fg="red", command=lambda: self.deliver_in_transit_packets()
		#	)
		#self.button.pack(side='left')
		
		
		# Button displaying original requests still waiting 
		#self.button = tk.Button(
		#	self.frame, text="Status", fg="red", command=lambda: self.status()
		#	)
		#self.button.pack(side='left')
		
		#
		#self.button = tk.Button(
		#	self.frame, text="Run", fg="red", command=lambda: self.simulation()
		#	)
		#self.button.pack(side='left')
		
		
		
		self.button = tk.Button(
			self.frame, text="Publish Content", fg="red", command=lambda: self.prepare()
			)
		self.button.pack(side='left')

		#self.button = tk.Button(
		#	self.frame, text="Initiate", fg="red", command=lambda: self.initiate()
		#	)
		#self.button.pack(side='left')

		#self.button = tk.Button(
		#	self.frame, text="In transit", fg="red", command=lambda: self.in_transit()
		#	)
		#self.button.pack(side='left')

		self.button = tk.Button(
			self.frame, text="Play", fg="red", command=lambda: self.play()
			)
		self.button.pack(side='left')

		self.button = tk.Button(
			self.frame, text="Pause", fg="red", command=lambda: self.pause()
			)
		self.button.pack(side='left')
		####

		#self.set_buttons()
		self.button = tk.Button(
			self.frame, text="QUIT", fg="red", command=lambda: self.quit()
			)
		self.button.pack(side='left')


		#self.set_buttons()
		self.button = tk.Button(
			self.frame, text="DDoS", fg="red", command=lambda: self.DDoS()
			)
		self.button.pack(side='left')


		self.pressed_label = tk.Label(
			self.frame, textvariable=self.button_pressed
			)
		self.pressed_label.pack(side='right')


		self.entry1 = tk.Entry(self.frame, textvariable=self.entry_value)
		self.entry1.pack()

		self.b = tk.Button(self.frame, text="Highlight", width=10, command=lambda: self.highlight())
		self.b.pack()

		self.b = tk.Button(self.frame, text="Regions", width=10, command=lambda: self.test_regions())
		self.b.pack()

		#self.button = tk.Button(
		#	self.frame, text="Flood", fg="red", command=lambda: self.aim()
		#	)
		#elf.button.pack(side='left')

		 ####
		self.canvas.create_window(0, 0, anchor='nw', window=self.frame)
		self.frame.update_idletasks()
		self.canvas.config(scrollregion=self.canvas.bbox("all"))
		#self.canvas.update()
		self.root.after(1, self.animation)
		self.root.mainloop()
		####


	def test_regions(self):
		for region in self.regions:
			print region
			for i in region:
				print i
				self.canvas.itemconfig(self.nodes[i].canvas_id, outline='purple', width=2.0)
				self.canvas.itemconfig(self.nodes[self.get_actual_node(i)].canvas_id, outline='purple', width=2.0)
				self.canvas.update()
			sleep(self.delay/1000)
			for i in range(1,7):
				self.canvas.itemconfig(self.nodes[i].canvas_id, outline='grey', width=1.0)
				self.canvas.itemconfig(self.nodes[self.get_actual_node(i)].canvas_id, outline='grey', width=1.0)
				self.canvas.update()

	def highlight(self):
		""" Used for highlighting a single node """
		node_id = int(self.entry_value.get())
		self.entry_value.set(node_id)
		print node_id
		self.canvas.itemconfig(self.nodes[node_id].canvas_id, outline='purple', width=2.0)
		self.canvas.itemconfig(self.nodes[self.get_actual_node(node_id)].canvas_id, outline='purple', width=2.0)
		self.canvas.update()
		self.root.after(2000, self.unhighlight, node_id)
		
		
		""" Used for highlighting a region of nodes 
		region = int(self.entry_value.get())
		self.entry_value.set(region)
		print region
		for i in range(1,7):
			self.canvas.itemconfig(self.nodes[self.regions[region][i]].canvas_id, outline='purple', width=2.0)
			self.canvas.itemconfig(self.nodes[self.get_actual_node(self.regions[region][i])].canvas_id, outline='purple', width=2.0)
			#self.canvas.update()
		sleep(self.delay/1000)
		for i in range(1,7):
			self.canvas.itemconfig(self.nodes[self.regions[region][i]].canvas_id, outline='grey', width=1.0)
			self.canvas.itemconfig(self.nodes[self.get_actual_node(self.regions[region][i])].canvas_id, outline='grey', width=1.0)
			#self.canvas.update()
		"""

	def unhighlight(self,node_id):
		self.canvas.itemconfig(self.nodes[node_id].canvas_id, outline='grey', width=1.0)
		self.canvas.itemconfig(self.nodes[self.get_actual_node(node_id)].canvas_id, outline='grey', width=1.0)
		self.canvas.update()

	def DDoS(self):
		DDoS_region = random.randint(0,len(self.regions)-1)
		content_name = self.content_names[random.randint(0,len(self.content_names)-1)]
		self._DDoS(DDoS_region, content_name, self.ammo)
		self.root.after(10000, self.DDoS_follow_up, DDoS_region, content_name)
		

	def _DDoS(self, region_id,content_name, size ):
		#i = 0 
		#while i < size:
		node_id = self.regions[region_id][random.randint(1,6)]
		self.enqueue_to_incoming(node_id, {'content_name': content_name, 'from_id':0, '_type': 'request', 'size': 1})
		color_dict = self.get_color(node_id)
		canvas_id = self.nodes[node_id].canvas_id
		self.canvas.itemconfig(canvas_id, outline=color_dict['color'], width=color_dict['width'])
		#self.canvas.itemconfig(self.nodes[self.get_actual_node(node_id)].canvas_id, outline=color_dict['color'], width=color_dict['width'])
			#i += 1
		self.canvas.update()
		self.root.after(1, self._DDoS, region_id, content_name, size)

	def DDoS_follow_up(self, DDoS_region, content_name):
		#selectable_regions = range(0,DDoS_region) + range(DDoS_region+1,len(self.regions))
		#selected_region = random.choice(selectable_regions)
		selected_region = 2
		node_id = self.regions[selected_region][0]
		self.enqueue_to_incoming(node_id, {'content_name': content_name, 'from_id':0, '_type': 'request', 'size': 1} )
		color_dict = self.get_color(node_id)
		self.canvas.itemconfig(self.nodes[node_id].canvas_id, outline=color_dict['color'], width=color_dict['width'])
		



	def pressed(self, button):
		self.button_pressed.set(str(button))
		self.frame.update()


	def update_delay(self, new_value):
		val = new_value[0]
		val = int(val)
		if val == 0:
			self.delay = 100
		else:
			self.delay = val * 1000
		#print self.delay

	def play(self):
		self.flag = True
		self.root.after_idle(self.animation)
		logging.debug(' Pressed: PLAY')
		self.button_pressed.set('PLAYING')
		self.frame.update()


	def pause(self):
		self.flag = False
		logging.debug(' Pressed: PAUSE')
		self.button_pressed.set('PAUSED')
		self.frame.update()


	def animation(self):
		if self.flag:
			self.root.after_idle(self.draw)
			delay = self.delay
			self.step()  # Does a process and deliver
			self.deliver_in_transit_packets()
			self.root.after(delay,self.animation)

			#self.root.after(delay,self.aim)
		
	def in_transit(self):
		logging.debug(' packets in transit: %s', str(self.in_transit_packets))

	def draw(self):
		# draw the board according to the current state
		 self.canvas.update_idletasks()
		# arrange for the next frame to draw in 4 seconds
		
		 
	def quit(self):
		self.end_program
		sys.exit()
		
	def status(self):
		""" Used for debugging """
		logging.debug(' Requests still awaiting content %s', str(self.active_requests))
	
	def test_nums(self):
		""" Displays whether nodes where numbered correctly """
		for i in range(1,100):
			print i
			self.canvas.itemconfig(self.nodes[i].canvas_id, outline='yellow', width=2.0)
			self.canvas.update_idletasks()
			self.canvas.itemconfig(self.nodes[i].canvas_id, outline='grey', width=1.0)
			self.canvas.update_idletasks()
			
	def prepare(self):
		c = 10000
		## HARD CODED -> 1 object per leaf -> 2458 content objects
		leaf_id = 2800
		while (leaf_id > 400 and self.flag):
			content_name = str(c)
			self.publish_content(content_name, content_name, leaf_id)
			self.content_names.append(content_name)
			c +=1
			leaf_id -= 5
		logging.debug('  Publishing complete. avail content_names are : %s ', str(self.content_names))
		self.button_pressed.set("PLAYING")
		self.frame.update()
				
			
	def initiate(self):
		node_id = self.upper_lim
		count = 0
		while node_id > 400:  ## HARD CODED; currently initiating 40% of network
			content_name = self.content_names[random.randint(0,(len(self.content_names)-1))]
			#self.nodes[node_id].incoming.append({'content_name': content_name, 'from_id':0, '_type': 'request' })  # 0 signifies that it is the source of request
			self.enqueue_to_incoming(node_id, {'content_name': content_name, 'from_id':0, '_type': 'request', 'size':1 })
			self.canvas.itemconfig(self.nodes[node_id].canvas_id, outline='blue', width=2.0)
			#self.active_requests[node_id] = {content_name:1} #1 is a dummy holder
			node_id -= 110
		self.canvas.update_idletasks()
		logging.debug('  Simulation ready')
		#self.step()


	def reload(self, ammo):
		self.ammo = int(ammo)

	def aim(self,number_of_targets=1):
		i = 0
		while i < number_of_targets:
			try:
				content_name = self.content_names[random.randint(0,(len(self.content_names)-1))]
				self.fire(random.randint(self.lower_lim,self.upper_lim), self.ammo, content_name)
			except ValueError:
				pass
			i += 1


	#firing amount 'size' packets all at same time
	def fire(self, node_id, size, content_name):
		if size > 0:
			self.enqueue_to_incoming(node_id, {'content_name': content_name, 'from_id':0, '_type': 'request', 'size': 1})
			color_dict = self.get_color(node_id)
			self.canvas.itemconfig(self.nodes[node_id].canvas_id, outline=color_dict['color'], width=color_dict['width'])
			self.canvas.itemconfig(self.nodes[self.get_actual_node(node_id)].canvas_id, outline=color_dict['color'], width=color_dict['width'])
			self.root.after_idle(self.fire, node_id, size-1, content_name)

	def enqueue_to_incoming(self, node_id, packet):
		self.nodes[node_id].total_load += packet['size']
		self.nodes[node_id].incoming.append(packet)
		
	def simulation(self):
		if (not is_empty(self.active_requests)):
			logging.debug('  Active requests are: %s', str(self.active_requests))
			self.step()
			self.deliver_in_transit_packets()
			self.root.after_idle(self.draw)
			#self.root.after(1, self.rand_request)
			self.root.after_idle(self.simulation)
			self.root.after_idle(self.reload)

		logging.debug(' No Network Activity')
		logging.debug('  Active requests are: %s', str(self.active_requests))
		
	def step(self):
		for n in reversed(range(1, len(self.nodes))):
			self.process(n)       
		#self.deliver_in_transit_packets()


	def assemble_regions(self):
		node_id = self.lower_lim
		while node_id in range(self.lower_lim,self.upper_lim):
			region = []
			for i in range(0,7):
				region.append(node_id)
				node_id += 1
			self.regions.append(region)


	def rand_request(self):
		node_id = random.randint(self.lower_lim,self.upper_lim+1)
		self.root.after(1, self._rand_request(node_id,20))

	def _rand_request(self,node_id, n):
		content_name = self.content_names[random.randint(0,len(self.content_names))] ## hard coded
		self.nodes[node_id].incoming.append({'content_name': content_name, 'from_id':0, '_type': 'request' })
		self.active_requests[node_id] = {content_name:1}
		self.root.after(1, self._rand_request(node_id, n-1))
			
	
	def begin_initial_request(self, content_name, _id):
		# Run Simulation
		logging.debug(' Initializing Simulation ...')
		source_id = _id
		logging.debug(' Initializing request for %s at node %d', content_name, source_id)
		self.nodes[source_id].incoming.append({'content_name': content_name, 'from_id':0, '_type': 'request' })  # 0 signifies that it is the source of request
		logging.debug('  Simulation ready: ')
		self.canvas.itemconfig(self.nodes[source_id].canvas_id, outline='blue', width=2.0)
		#self.canvas.update_idletasks()
		self.active_requests[_id] = {content_name:1} #1 is a dummy holder
	
	
	def end_program(self):
		self.root.destroy()
	
	def get_other_leaf_machine(self,node_id):
		x = node_id
		while x == node_id:
			x = random.randint(self.lower_lim, self.upper_lim)
		return x


	def get_random_leaf_machine(self):
		return random.randint(self.lower_lim, self.upper_lim)
	
	def publish_content( self,content_name, content_data, dest_id):
		####dest_id hard coded right now, random
		#dest_id = self.get_random_leaf_machine()
		#logging.debug(' Publishing content: (%s)  to  node %d', content_name, dest_id)
		self.nodes[dest_id].content_store[content_name] =  content_data

		if self.delay > 500:
			self.canvas.itemconfig(self.nodes[dest_id].canvas_id, outline='purple', width=2.0)
			self.canvas.update()
			sleep(self.delay/1000)
			self.canvas.itemconfig(self.nodes[dest_id].canvas_id, outline='grey', width=1.0)
			self.canvas.update()


		#logging.debug(' Updating forwarding tables of parents of node %d ... ' % dest_id)
		# Get all parents of dest node until reaching root 1
		flag = False
		current = dest_id
		parent_id = self.get_parent(dest_id)
		while ( parent_id != 0 ):    # parent of 1 always returns 0
			self.nodes[parent_id].forwarding_table[content_name] = current
			if self.delay > 500:
				self.canvas.itemconfig(self.nodes[parent_id].canvas_id, outline='purple', width=2.0)
				self.canvas.itemconfig(self.nodes[self.get_actual_node(parent_id)].canvas_id, outline='purple', width=2.0)
				self.canvas.update()
				sleep(self.delay/1000)
				self.canvas.itemconfig(self.nodes[parent_id].canvas_id, outline='grey', width=1.0)
				self.canvas.itemconfig(self.nodes[self.get_actual_node(parent_id)].canvas_id, outline='grey', width=1.0)
				self.canvas.update()
			#logging.debug(' Updated forwarding table of node %d ' % parent_id)
			#logging.debug(' Forwarding table now is: %s', str(self.nodes[parent_id].forwarding_table))
			current = parent_id
			parent_id = self.get_parent(parent_id)
		#logging.debug(' Completed updating FT of parents of %d ' % dest_id)
	
	
	def get_child_at(self,direction, node_id):
		if (direction.lower() == 'c'):
			return 7*node_id + 1
		elif (direction.lower() == 'n'):
			return 7*node_id + 2
		elif (direction.lower() == 's'):
			return 7*node_id + 3
		elif (direction.lower() == 'ne'):
			return 7*node_id+ 4
		elif (direction.lower() == 'se'):
			return 7*node_id + 5
		elif (direction.lower() == 'nw'):
			return 7*node_id + 6
		elif (direction.lower() == 'sw'):
			return 7*node_id + 7
		else:
			return 'error'
	
	
	
	def get_parent(self, node_id):   
		n = node_id
		if n == 1: 
			return 0
		if (n <= 7):
			return 1 
		elif (n%7 == 1):
			return (n/7)
		else:
			return self.get_parent((n - ((n-1)%7))) #need one more level up because it was not a center node
	
	
	def get_actual_node(self,rep):
		curr = rep
		while  (curr < self.lower_lim):
			curr = self.get_child_at('c',curr)
		return curr
	
	def get_parent_and_actual(self, node_id):
		parent_id = self.get_parent(node_id)
		return [parent_id, get_actual_node(parent_id, self.levels)]
	
	def get_color(self, node_id):
		#size = len(self.nodes[node_id].incoming) #account for length of incoming
		size = self.nodes[node_id].total_load
		#for key in self.nodes[node_id].pending_table:     #account for size of awaiting requests
		#	size += len(self.nodes[node_id].pending_table[key])

		if node_id <= 8:
			if size <= 0:
				return {'color':'grey', 'width':1.0}
			elif size < 100:
				return {'color':'blue', 'width':2.0}
			elif size < 200:
				return {'color':'dark orange', 'width':2.0}
			elif size < 300:
				return {'color':'red', 'width':2.0}
		else:
			if size <= 0:
				return {'color':'grey', 'width':1.0}
			elif size < 5:
				return {'color':'blue', 'width':2.0}
			elif size < 75:
				return {'color':'dark orange', 'width':2.0}
			elif size < 101:
				return {'color':'red', 'width':2.0}
	
	def deliver_in_transit_packets(self):
		if( not is_empty(self.in_transit_packets)):
			packet = self.in_transit_packets.pop()
			dest_id = packet['dest_id']
			if dest_id == 0 :
				logging.warning(' invalid packet destination: %s', str(packet))
			else:
				#self.nodes[dest_id].incoming.append(packet) 
				self.enqueue_to_incoming(dest_id, packet)
				logging.debug(' Delivered packet from %d to %d', packet['from_id'], packet['dest_id'])
				#Update the edge color to the recipient
				color_dict = self.get_color(dest_id)
				canvas_id = self.nodes[dest_id].canvas_id
				#if self.canvas.itemcget(canvas_id, 'outline') != color_dict['color']:
				self.canvas.itemconfig(canvas_id, outline=color_dict['color'], width=color_dict['width'])
				self.canvas.itemconfig(self.nodes[self.get_actual_node(dest_id)].canvas_id, outline=color_dict['color'], width=color_dict['width'])
				#self.canvas.update_idletasks()
			self.root.after_idle(self.deliver_in_transit_packets)      
		

	def computation_power(self, node_id):
		if node_id <= 7:
			return 4
		elif node_id <= 56:
			return 3
		elif node_id <= 399:
			return 2
		else: 
			return 1
		
	def process(self, node_id):
		#logging.debug(' processing incoming packet at %d' % node_id)
		## Non leaf nodes run twice as fast 
		#if node_id < 343:
		#	iterations = 2
		#else:
		#	iterations = 1
		#i = 0
		#while i < iterations:
		#	i += 1
		comp_power = self.computation_power(node_id)
		i = 0 
		while i < comp_power:
			if (not is_empty(self.nodes[node_id].incoming)):
				logging.debug(' processing incoming packet at %d' % node_id)
				packet = self.nodes[node_id].incoming.popleft()
				self.nodes[node_id].total_load -= packet['size']
				pack = str(packet)
				logging.debug(" packet data: %s", pack) 
				
				#Update the color now that we popped an incoming packet
				""" TODO: TEST LOCATION OF THIS BLOCK"""
				color_dict = self.get_color(node_id)
				self.canvas.itemconfig(self.nodes[node_id].canvas_id, outline=color_dict['color'], width=color_dict['width'])
				self.canvas.itemconfig(self.nodes[self.get_actual_node(node_id)].canvas_id, outline=color_dict['color'], width=color_dict['width'])


				if packet['_type'] == 'request':
					# Packet is a request      
					content_name = packet['content_name']
					requester_id = packet['from_id']    
					
					# Case 1: content in cache
					if content_name in self.nodes[node_id].content_store:
						if requester_id == 0:
							logging.debug(" DONE! Content already cached, I am the source: %d" % node_id)
							# Case where active request hasnt been created yet but content in cache
							try: 
								del self.active_requests[node_id][content_name] 
								if len(self.active_requests[node_id])==0:
									del self.active_requests[node_id]
							except KeyError:
								pass
						else:
							self.nodes[node_id].outgoing_packet({ 'content_name': content_name, 'from_id':node_id,
																 'content_data':self.nodes[node_id].content_store[content_name], 
																 'dest_id':requester_id, '_type':'response', 'size':1},
																 self.in_transit_packets)
							logging.debug(" content %s already in cache", content_name) 
							logging.debug(" sent content back to  %d ", requester_id)
							
					# Case 2: duplicate request exists
					elif content_name in self.nodes[node_id].pending_table:   
						self.nodes[node_id].pending_table[content_name] += [requester_id]
						#logging.debug(" duplicate request for content %s , added requester_id %d to PT", packet[content_name], packet[requester_id]) 
						logging.debug(" duplicate request for content , added requester_id to PT") 
						#if (requester_id == 0):
					  	#	self.active_requests[node_id] = {content_name:1}
						
					# Case 3: no pending request, but location lives in children, create entry in PT, send request to child
					elif content_name in self.nodes[node_id].forwarding_table:
						directed_child_id  = self.nodes[node_id].forwarding_table[content_name]   #direction of child where destination node is contained 
						self.nodes[node_id].pending_table[content_name] = [requester_id]          # entry in PT created
						self.nodes[node_id].outgoing_packet( {'content_name': content_name , 'dest_id':directed_child_id, 
															  'from_id': node_id, '_type': 'request', 'size':1}, self.in_transit_packets)
						logging.debug(" location content %s known, entry for requester %d created in PT", content_name, requester_id) 
						logging.debug(" forwarded request to child %d ", directed_child_id )
						#if (requester_id == 0):
					  	#	self.active_requests[node_id] = {content_name:1}

					# Case 4: no duplicate, add to PT, forward to parent 
					else:
						self.nodes[node_id].pending_table[content_name] = [requester_id]
						parent_id = self.get_parent(node_id)
						self.nodes[node_id].outgoing_packet({'content_name':content_name, 'from_id':node_id,
															 'dest_id': parent_id, "_type": 'request', 'size':1 }, self.in_transit_packets)
						logging.debug(" content %s NOT known, entry for requester %d created in PT, sent request to parent %d", content_name, requester_id, parent_id) 
					  	# IF this is the source then add to active_requests
					  	if (requester_id == 0):
					  		self.active_requests[node_id] = {content_name:1}



				elif packet['_type'] == 'response':
					# packet is a response
					content_name = packet['content_name']
					data = packet['content_data']    

					# Case 1: node is source of request, 0 signifies it is the source of request
					if ((0 in self.nodes[node_id].pending_table[content_name]) and (len(self.nodes[node_id].pending_table[content_name])==1)):
						logging.debug(" DONE! I am the source: %d" % node_id)
						self.nodes[node_id].content_store[content_name] = data
						logging.debug(" Added content (%s) to content store"  % content_name)
						del self.nodes[node_id].pending_table[content_name]
						logging.debug(" Deleted content (%s) from PT"  % content_name)
						# Remove from the networks active requests monitor
						try:
							del self.active_requests[node_id][content_name] 
							if len(self.active_requests[node_id])==0:
								del self.active_requests[node_id]
							del self.nodes[node_id].pending_table[content_name]
							logging.debug(" Deleted content (%s) from PT"  % content_name)
						except KeyError:
							pass
					# Case 2: node was a middle man
					else:
						print logging.debug("Forwarding response along to all requesters, I am: %d ... ", node_id)
						for dest_id in self.nodes[node_id].pending_table[content_name]:
							if dest_id == 0:
								logging.debug(" DONE! I am a source: %d" % node_id)
							else:
								self.nodes[node_id].outgoing_packet({'content_name':packet['content_name'], 'from_id':node_id, 
																	 'content_data':data, '_type':'response', 'dest_id':dest_id, 'size':1},
																	self.in_transit_packets )
								logging.debug("Sent response to requester %d ", dest_id)
								logging.debug("Forwarding to all requesters complete")

						del self.nodes[node_id].pending_table[content_name]
						logging.debug(" Deleted content (%s) from PT"  % content_name)
						self.nodes[node_id].content_store[packet['content_name']] = data
						logging.debug(" Added content (%s) to content store"  % content_name)

					color_dict = self.get_color(node_id)
					self.canvas.itemconfig(self.nodes[node_id].canvas_id, outline=color_dict['color'], width=color_dict['width'])
					self.canvas.itemconfig(self.nodes[self.get_actual_node(node_id)].canvas_id, outline=color_dict['color'], width=color_dict['width'])

				else:
					logging.warning(' Mislabeled Packet')
					color_dict = self.get_color(node_id)
					self.canvas.itemconfig(self.nodes[node_id].canvas_id, outline=color_dict['color'], width=color_dict['width'])
					self.canvas.itemconfig(self.nodes[self.get_actual_node(node_id)].canvas_id, outline=color_dict['color'], width=color_dict['width'])
			i += 1
	
	
	def build(self, levels):
		self._build(levels, 0, 150, 550, 540)
	
	def _build(self, level,i,r,x,y):
		""" Helper function for build() """
		#center = 7i+1
		#north = 7i+2
		#south = 7i+3
		#northaast = 7i+4
		#southeast = 7i+5
		#northwest = 7i+6
		#southwest = 7i+7
	
	  
		if level > 0:

			#center
			canvas_id = self.canvas.create_circle(x, y , r, outline = 'grey', width = 1.0, tags=str(7*i+1))
			self.nodes[7*i+1] = Servers.NBServer(7*i+1, canvas_id)
			self.canvas.create_circle(x, y , r, outline = 'grey', width = 1.0, tags=str(7*i+1))
			self.root.after(0, self._build(level-1,7*i+1,r/3,x,(y)))

			#north
			canvas_id = self.canvas.create_circle(x, (y-(2.0*r)) , r, outline = 'grey', width = 1.0, tags=str(7*i+2))
			self.nodes[7*i+2] = Servers.NBServer(7*i+2, canvas_id)
			self.root.after(0, self._build(level-1,7*i+2,r/3,x,(y-(2.0*r))))

			#south
			canvas_id = self.canvas.create_circle(x, (y+(2.0*r)) , r, outline = 'grey', width = 1.0, tags=str(7*i+3))
			self.nodes[7*i+3] = Servers.NBServer(7*i+3, canvas_id)
			self.root.after(0, self._build(level-1,7*i+3,r/3,x,(y+(2.0*r))))

			#northeast
			canvas_id = self.canvas.create_circle(x+2*r*math.sqrt(3)/2, (y-r) , r, outline = 'grey', width = 1.0, tags=str(7*i+4))            
			self.nodes[7*i+4] = Servers.NBServer(7*i+4, canvas_id)
			self.root.after(0, self._build(level-1,7*i+4,r/3,x+2*r*math.sqrt(3)/2,(y-r)))

			#southeast
			canvas_id = self.canvas.create_circle(x+2*r*math.sqrt(3)/2, (y+r) , r, outline = 'grey', width = 1.0, tags=str(7*i+5))
			self.nodes[7*i+5] = Servers.NBServer(7*i+5, canvas_id)
			self.root.after(0, self._build(level-1,7*i+5,r/3,x+2*r*math.sqrt(3)/2,(y+r)))

			#northwest
			canvas_id = self.canvas.create_circle( x-2*r*math.sqrt(3)/2 , (y-r) , r, outline = 'grey', width = 1.0, tags=str(7*i+6))
			self.nodes[7*i+6] = Servers.NBServer(7*i+6, canvas_id)
			self.root.after(0, self._build(level-1,7*i+6,r/3,x-2*r*math.sqrt(3)/2,(y-r)))

			#southwest
			canvas_id = self.canvas.create_circle( x-2*r*math.sqrt(3)/2, (y+r) , r, outline = 'grey', width = 1.0, tags=str(7*i+7))
			self.nodes[7*i+7] = Servers.NBServer(7*i+7, canvas_id)
			self.root.after(0, self._build(level-1,7*i+7,r/3,x-2*r*math.sqrt(3)/2,(y+r)))
					
		else:
			if level == 0:
				#center
				canvas_id = self.canvas.create_circle(x, y , r, outline = 'grey', width = 1.0, tags=str(7*i+1))
				self.nodes[7*i+1] = Servers.NBServer(7*i+1, canvas_id)
				
				#north
				canvas_id = self.canvas.create_circle(x, (y-(2.0*r)) , r, outline = 'grey', width = 1.0, tags=str(7*i+2))
				self.nodes[7*i+2] = Servers.NBServer(7*i+2, canvas_id)
			   
				#south
				canvas_id = self.canvas.create_circle(x, (y+(2.0*r)) , r, outline = 'grey', width = 1.0, tags=str(7*i+3))
				self.nodes[7*i+3] = Servers.NBServer(7*i+3, canvas_id)

				#northeast
				canvas_id = self.canvas.create_circle(x+2*r*math.sqrt(3)/2, (y-r), r, outline = 'grey', width = 1.0, tags=str(7*i+4))
				self.nodes[7*i+4] = Servers.NBServer(7*i+4, canvas_id)
			   
				#southeast
				canvas_id = self.canvas.create_circle(x+2*r*math.sqrt(3)/2, (y+r) , r, outline = 'grey', width = 1.0, tags=str(7*i+5))
				self.nodes[7*i+5] = Servers.NBServer(7*i+5, canvas_id)
			  
				#northwest
				canvas_id = self.canvas.create_circle(x-2*r*math.sqrt(3)/2, (y-r) , r, outline = 'grey', width = 1.0, tags=str(7*i+6))
				self.nodes[7*i+6] = Servers.NBServer(7*i+6, canvas_id)
			   

				#southwest
				canvas_id = self.canvas.create_circle(x-2*r*math.sqrt(3)/2, (y+r) , r, outline = 'grey', width = 1.0, tags=str(7*i+7))
				self.nodes[7*i+7] = Servers.NBServer(7*i+7, canvas_id)
				
			
				
root = tk.Tk()
Network(3, root) 
root.mainloop()