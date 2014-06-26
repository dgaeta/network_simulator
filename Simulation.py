import Tkinter as tk
from time import sleep
import math
import logging
import Servers 
import random
import sys
from Utilities import *

logging.getLogger().setLevel(logging.DEBUG)

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler


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
		self.simulation_state = tk.StringVar()
		self.simulation_state.set('PLAYING')
		self.regions = []
		self.highlight_entry = tk.StringVar()
		self.radius = 150
		self.zoom_level = 0
		####
		
		
		#### GUI for network sim 
		self.root = master

		# Give the window scrolls
		vscrollbar = AutoScrollbar(self.root)
		vscrollbar.grid(row=0, column=3, sticky='n'+'s')
		hscrollbar = AutoScrollbar(self.root, orient='horizontal')
		hscrollbar.grid(row=2, column=0, sticky='e'+'w')

		self.frame = tk.Frame(self.root, height=600,width=900, relief='raised', bd=2)
		self.frame.grid(row=0,column=0)
		self.frame.grid_rowconfigure(0, weight=0)
		self.frame.grid_columnconfigure(0, weight=1)

		self.canvas = tk.Canvas(self.root,width=825,height=600,
                yscrollcommand=vscrollbar.set,
                xscrollcommand=hscrollbar.set)
		self.canvas.grid(row=1, column=0, sticky='e'+'w'+'n'+'s' )
		self.canvas.grid_columnconfigure(0, weight=1)
		self.canvas.grid_rowconfigure(1, weight=1)

		vscrollbar.config(command=self.canvas.yview)
		hscrollbar.config(command=self.canvas.xview)

		# make the frame not expandable
		self.root.grid_rowconfigure(0, weight=0, minsize=150)
		self.root.grid_columnconfigure(0, weight=0, minsize=700)
		# make the canvas expandable
		self.root.grid_rowconfigure(1, weight=1, minsize=150)
		self.root.grid_columnconfigure(0, weight=1, minsize=700)
		

		# heatmap image 
		photo = tk.PhotoImage(file="heat1.gif")
		self.label = tk.Label(
			self.frame, text="Machine Load", image=photo, anchor='w', justify='left', compound=tk.BOTTOM)
		self.label.photo = photo
		self.label.grid(row=3,column=1, columnspan=4,padx=20)

		# label for simulatoin state
		self.simulation_state_label = tk.Label(
			self.frame, textvariable=self.simulation_state
			)
		self.simulation_state_label.grid(row=2,column=1)

		# delay in seconds of animation
		self.delay_scale = tk.Scale(
			self.frame, from_=0, to=5, orient='horizontal', command=self.update_delay, label='Animation Delay', length=150
			)
		self.delay_scale.set(5)
		self.delay_scale.grid(row=0,column=0)

		# Degree of stress on network nodes
		self.request_freq = tk.Scale(
			self.frame, from_=0, to=100, orient='horizontal', command=self.reload, label='Network Activity', length=150
			)
		self.request_freq.set(30)
		self.request_freq.grid(row=1,column=0)

		self.button = tk.Button(
			self.frame, text="PLAY", fg="red", command=lambda: self.play()
			)
		self.button.grid(row=0,column=1)

		self.button = tk.Button(
			self.frame, text="PAUSE", fg="red", command=lambda: self.pause()
			)
		self.button.grid(row=0,column=2)		####

		#self.set_buttons()
		self.button = tk.Button(
			self.frame, text="QUIT", fg="red", command=lambda: self.quit()
			)
		self.button.grid(row=0,column=3)

		# zoom in
		self.zoom_button = tk.Button(
			self.frame, text="ZOOM +", command=lambda: self.redraw('in'))
		self.zoom_button.grid(row=0,column=4, sticky='n')

		# zoom out 
		self.zoom_button = tk.Button(
			self.frame, text="ZOOM -", command=lambda: self.redraw('out'))
		self.zoom_button.grid(row=0,column=4, sticky='s')
		
		self.entry1 = tk.Entry(
			self.frame, textvariable=self.highlight_entry)
		self.entry1.insert(0, "enter node number")
		self.entry1.grid(row=0,column=5, sticky='n')

		self.highlight_button = tk.Button(
			self.frame, text="Highlight Node", width=10, command=lambda: self.highlight())
		self.highlight_button.grid(row=0,column=5,sticky='s')

		self.regions_button = tk.Button(
			self.frame, text="Show Region", width=10, command=lambda: self.illustrate_regions())
		self.regions_button.grid(row=1,column=5, sticky='n')

		self.regions_button = tk.Button(
			self.frame, text="Show Publish", width=10, command=lambda: self.illustrate_publish())
		self.regions_button.grid(row=1,column=5, sticky='s')

		self.regions_button = tk.Button(
			self.frame, text="Show Request", width=10, command=lambda: self.illustrate_request())
		self.regions_button.grid(row=1,column=5, sticky='n')

		self.button = tk.Button(
			self.frame, text="DDoS", fg="red", width=10, command=lambda: self.DDoS()
			)
		self.button.grid(row=2,column=5, sticky='s')





		## Enqueue the build into the mainloop
		self.root.after(0, self.build(levels))
		##
		self.root.after_idle(self.assemble_regions)	

		self.frame.update_idletasks()
		self.canvas.config(scrollregion=self.canvas.bbox("all"))
		self.root.after_idle(self.prepare)
		self.root.after_idle(self.animation)
		self.root.mainloop()
		####


	
	def redraw(self, method):
		if method == 'in':
			self.radius *= 1.2
			self.zoom_level += 1
		else:
			self.radius *= .8
			self.zoom_level -= 1
		self.pause()
		self.canvas.delete('all')
		self._redraw(self.levels, 0, self.radius, 600, 540)
		bounds = self.canvas.bbox('all')  # returns a tuple like (x1, y1, x2, y2)
		width = bounds[2] - bounds[0]
		height = bounds[3] - bounds[1]
		self.canvas.config(scrollregion=self.canvas.bbox("all"))
		self.canvas.update()
		self.play()
	
	def _redraw(self, level,i,r,x,y):
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
			color_width = self.get_color(7*i+1)
			canvas_id = self.canvas.create_circle(x, y , r, outline = color_width['color'], width = color_width['width'])
			self.nodes[7*i+1].canvas_id = canvas_id
			self.root.after(0, self._build(level-1,7*i+1,r/3,x,(y)))

			#north
			color_width = self.get_color(7*i+2)
			canvas_id = self.canvas.create_circle(x, (y-(2.0*r)) , r, outline = color_width['color'], width = color_width['width'])
			self.nodes[7*i+2].canvas_id = canvas_id
			self.root.after(0, self._build(level-1,7*i+2,r/3,x,(y-(2.0*r))))

			#south
			color_width = self.get_color(7*i+3)
			canvas_id = self.canvas.create_circle(x, (y+(2.0*r)) , r, outline = color_width['color'], width = color_width['width'])
			self.nodes[7*i+3].canvas_id = canvas_id
			self.root.after(0, self._build(level-1,7*i+3,r/3,x,(y+(2.0*r))))

			#northeast
			color_width = self.get_color(7*i+4)
			canvas_id = self.canvas.create_circle(x+2*r*math.sqrt(3)/2, (y-r) , r, outline = color_width['color'], width = color_width['width'])            
			self.nodes[7*i+4].canvas_id = canvas_id
			self.root.after(0, self._build(level-1,7*i+4,r/3,x+2*r*math.sqrt(3)/2,(y-r)))

			#southeast
			color_width = self.get_color(7*i+5)
			canvas_id = self.canvas.create_circle(x+2*r*math.sqrt(3)/2, (y+r) , r, outline = color_width['color'], width = color_width['width'])
			self.nodes[7*i+5].canvas_id = canvas_id
			self.root.after(0, self._build(level-1,7*i+5,r/3,x+2*r*math.sqrt(3)/2,(y+r)))

			#northwest
			color_width = self.get_color(7*i+6)
			canvas_id = self.canvas.create_circle( x-2*r*math.sqrt(3)/2 , (y-r) , r, outline = color_width['color'], width = color_width['width'])
			self.nodes[7*i+6].canvas_id = canvas_id
			self.root.after(0, self._build(level-1,7*i+6,r/3,x-2*r*math.sqrt(3)/2,(y-r)))

			#southwest
			color_width = self.get_color(7*i+7)
			canvas_id = self.canvas.create_circle( x-2*r*math.sqrt(3)/2, (y+r) , r, outline = color_width['color'], width = color_width['width'])
			self.nodes[7*i+7].canvas_id = canvas_id
			self.root.after(0, self._build(level-1,7*i+7,r/3,x-2*r*math.sqrt(3)/2,(y+r)))
					
		else:
			if level == 0:
				#center
				color_width = self.get_color(7*i+1)
				canvas_id = self.canvas.create_circle(x, y , r, outline = color_width['color'], width = color_width['width'])
				self.nodes[7*i+1].canvas_id = canvas_id
				
				
				#north
				color_width = self.get_color(7*i+2)
				canvas_id = self.canvas.create_circle(x, (y-(2.0*r)) , r, outline = color_width['color'], width = color_width['width'])
				self.nodes[7*i+2].canvas_id = canvas_id
			   
				#south
				color_width = self.get_color(7*i+3)
				canvas_id = self.canvas.create_circle(x, (y+(2.0*r)) , r, outline = color_width['color'], width = color_width['width'])
				self.nodes[7*i+3].canvas_id = canvas_id

				#northeast
				color_width = self.get_color(7*i+4)
				canvas_id = self.canvas.create_circle(x+2*r*math.sqrt(3)/2, (y-r) , r, outline = color_width['color'], width = color_width['width'])            
				self.nodes[7*i+4].canvas_id = canvas_id
			
				   
				#southeast
				color_width = self.get_color(7*i+5)
				canvas_id = self.canvas.create_circle(x+2*r*math.sqrt(3)/2, (y+r) , r, outline = color_width['color'], width = color_width['width'])
				self.nodes[7*i+5].canvas_id = canvas_id
				
  
				#northwest
				color_width = self.get_color(7*i+6)
				canvas_id = self.canvas.create_circle( x-2*r*math.sqrt(3)/2 , (y-r) , r, outline = color_width['color'], width = color_width['width'])
				self.nodes[7*i+6].canvas_id = canvas_id
				

				#southwest
				color_width = self.get_color(7*i+7)
				canvas_id = self.canvas.create_circle( x-2*r*math.sqrt(3)/2, (y+r) , r, outline = color_width['color'], width = color_width['width'])
				self.nodes[7*i+7].canvas_id = canvas_id
				

	def illustrate_regions(self):
		region = self.regions[11]

		self.canvas.itemconfig(self.nodes[region[0]].canvas_id, outline='purple', width=2.0)
		self.canvas.itemconfig(self.nodes[self.get_actual_node(region[0])].canvas_id, outline='purple', width=2.0)
		self.canvas.update_idletasks()
		sleep(2)
		self.canvas.itemconfig(self.nodes[region[0]].canvas_id, outline='grey', width=1.0)
		self.canvas.itemconfig(self.nodes[self.get_actual_node(region[0])].canvas_id, outline='grey', width=1.0)
		self.canvas.update_idletasks()
		

		for i in range(1,7):
				self.canvas.itemconfig(self.nodes[region[i]].canvas_id, outline='purple', width=2.0)
				self.canvas.itemconfig(self.nodes[self.get_actual_node(region[i])].canvas_id, outline='purple', width=2.0)
				self.canvas.update_idletasks()
		sleep(2)
		for i in range(1,7):
				self.canvas.itemconfig(self.nodes[region[i]].canvas_id, outline='grey', width=1.0)
				self.canvas.itemconfig(self.nodes[self.get_actual_node(region[i])].canvas_id, outline='grey', width=1.0)
				self.canvas.update_idletasks()


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
		node_id = int(self.highlight_entry.get())
		self.highlight_entry.set(node_id)
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
		DDoS_region = self.regions[random.randint(0,len(self.regions)-1)]
		content_name = self.content_names[random.randint(0,len(self.content_names)-1)]
		self._DDoS(DDoS_region, content_name, self.ammo)
		#self.root.after(10000, self.DDoS_follow_up, DDoS_region, content_name)
		

	def _DDoS(self, region_nodes,content_name, size ):
		#i = 0 
		node_id = region_nodes[random.randint(1,6)]
		#print node_id
		self.enqueue_to_incoming(node_id, {'content_name': content_name, 'from_id':0, '_type': 'request', 'size': 1})
		color_dict = self.get_color(node_id)
		canvas_id = self.nodes[node_id].canvas_id
		try:
			self.canvas.itemconfig(canvas_id, outline=color_dict['color'], width=color_dict['width'])
		except TypeError:
			self.pause()
			print node_id
			print str(color_dict)
		#self.canvas.itemconfig(self.nodes[self.get_actual_node(node_id)].canvas_id, outline=color_dict['color'], width=color_dict['width'])
			#i += 1
		self.canvas.update_idletasks()
		self.root.after(1, self._DDoS, region_nodes, content_name, size)

	def DDoS_follow_up(self, DDoS_region, content_name):
		#selectable_regions = range(0,DDoS_region) + range(DDoS_region+1,len(self.regions))
		#selected_region = random.choice(selectable_regions)
		selected_region = 2
		node_id = self.regions[selected_region][0]
		self.enqueue_to_incoming(node_id, {'content_name': content_name, 'from_id':0, '_type': 'request', 'size': 1} )
		color_dict = self.get_color(node_id)
		self.canvas.itemconfig(self.nodes[node_id].canvas_id, outline=color_dict['color'], width=color_dict['width'])
		

	def pressed(self, button):
		self.simulation_state.set(str(button))
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
		self.root.after(self.delay,self.animation)
		logging.debug(' Pressed: PLAY')
		self.simulation_state.set('PLAYING')
		#self.frame.update_idletasks()


	def pause(self):

		logging.debug(' Pressed: PAUSE')
		self.simulation_state.set('PAUSED')
		#self.frame.update_idletasks()


	def animation(self):
		if self.simulation_state.get() == 'PLAYING':
			self.root.after_idle(self.draw)
			self.step()  # Does a process and deliver
			self.deliver_in_transit_packets()
			self.root.after(self.delay,self.animation)

			#self.root.after(delay,self.aim)
		
	def in_transit(self):
		logging.debug(' packets in transit: %s', str(self.in_transit_packets))

	def draw(self):
		# draw the board according to the current state
		 self.canvas.update_idletasks()
		# arrange for the next frame to draw in 4 seconds
		
		 
	def quit(self):
		self.flag = False
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
		content_index = 10000
		## HARD CODED -> 1 object per leaf -> 2458 content objects
		leaf_id = 2800
		while (leaf_id > 450 and self.flag):
			content_name = str(content_index)
			self.publish_content(content_name, content_name, leaf_id)
			self.content_names.append(content_name)
			content_index +=1
			leaf_id -= 5
		logging.debug('  Publishing complete. avail content_names are %d through %d ', int(self.content_names[0]), 
			int(self.content_names[(len(self.content_names) -1)]))
		self.simulation_state.set("PLAYING")
		self.frame.update_idletasks()
				

	def publish_content( self,content_name, content_data, source_id):
		self.nodes[source_id].content_store[content_name] =  content_data
		
		# Update all parents hash of source node until reaching root 1
		current = source_id
		parent_id = self.get_parent(source_id)
		while ( parent_id != 0 ):    # get_parent of 1 always returns 0
			self.nodes[parent_id].forwarding_table[content_name] = current
			current = parent_id
			parent_id = self.get_parent(parent_id)
		#logging.debug(' Completed updating FT of parents of %d ' % dest_id)

			
	def illustrate_publish(self):
		source_id = 1000
		content_name = 'espn.com/usa-world-cup-winner'
		if self.delay > 500:
			self.canvas.itemconfig(self.nodes[source_id].canvas_id, outline='purple', width=2.0)
			self.canvas.update()
			sleep(self.delay/1000)
			self.canvas.itemconfig(self.nodes[source_id].canvas_id, outline='grey', width=1.0)
			self.canvas.update()
		
		# Get all parents of source node until reaching root 1
		current = source_id
		parent_id = self.get_parent(source_id)
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
			
			current = parent_id
			parent_id = self.get_parent(parent_id)
		#logging.debug(' Completed updating FT of parents of %d ' % dest_id)

		pass

	def illustrate_request(self):
		node_id = 2200
		content_name = '10454'
		self.enqueue_to_incoming(node_id, {'content_name': content_name, 'from_id':0, '_type': 'request', 'size': 1})
		color_dict = self.get_color(node_id)
		canvas_id = self.nodes[node_id].canvas_id
		self.canvas.itemconfig(canvas_id, outline=color_dict['color'], width=color_dict['width'])
		self.canvas.update()
		


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
			else: 
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
		self._build(levels, 0, 150, 600, 540)
	
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
root.wm_title("Name Based Routing Simulation")
Network(3, root) 
root.mainloop()