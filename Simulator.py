##
# Network Simulator to show behavior of Name Based Routing Algorithm
# 
#
# author: Daniel Gaeta 
# Name Based Routing Designed by: Armand Prieditis 
##

import Tkinter as tk
from time import sleep
import time
import math
import logging
import Routers 
import random
import sys
import numpy as np
import csv
import copy
from datetime import datetime
from apscheduler.scheduler import Scheduler
import atexit
from Routers import *

logging.getLogger().setLevel(logging.DEBUG)

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
#from matplotlib.backend_bases import key_press_handler



def is_empty( any_structure):
	if any_structure:
		#print('Structure is not empty.')
		return False
	else:
		#print('Structure is empty.')
		return True

def get_level(node_id):
		if node_id <= 7:
			return 0
		elif node_id <=56:
			return 1
		elif node_id <= 399:
			return 2
		elif node_id <= 2800:
			return 3
		else: 
			logging.debug('Incorrect Node ID given at get_level')


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
	def __init__( self, levels, gui_boolean):
		
		# data structs for the network, core data structures
		self.nodes = {}
		self.levels = levels
		self.lower_lim = 400
		self.upper_lim = ((7**(levels+1))-3)
		self.content_names = []
		self.regions = []
		self.total_round_trip_times = []
		self.rtt_slices = []
		self.level_congestion = {0:0, 1:0, 2:0, 3:0}
		self.total_congestions = []
		self.packets_to_be_delivered = []

		# data structures used for gui animation
		self.flag = True
		self.in_transit_packets = []
		self.delay = 500
		self.ammo = 0 
		self.simulation_state = ''
		self.root = ''
		self.highlight_entry = ''
		self.radius = 150
		self.zoom_level = 0
		
		self.gui_boolean = gui_boolean
		if self.gui_boolean:
			self.initialize_gui()
		else:
			self.build_without_gui(self.levels)
		
		
		
	## GUI for network sim 
	def initialize_gui(self):
		self.root = tk.Tk()
		self.simulation_state = tk.StringVar()
		self.simulation_state.set('PLAYING')
		self.highlight_entry = tk.StringVar()

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
			self.frame, from_=0, to=100, orient='horizontal', command=self.request_freq_callback, label='Network Activity', length=150
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
			self.frame, text="ZOOM +", command=lambda: self.zoom('in'))
		self.zoom_button.grid(row=0,column=4, sticky='n')

		# zoom out 
		self.zoom_button = tk.Button(
			self.frame, text="ZOOM -", command=lambda: self.zoom('out'))
		self.zoom_button.grid(row=0,column=4, sticky='s')
		
		self.entry1 = tk.Entry(
			self.frame, textvariable=self.highlight_entry)
		self.entry1.insert(0, "enter node number")
		self.entry1.grid(row=0,column=5, sticky='n')

		self.highlight_button = tk.Button(
			self.frame, text="Highlight", width=10, command=lambda: self.highlight())
		self.highlight_button.grid(row=0,column=5,sticky='s')

		self.regions_button = tk.Button(
			self.frame, text="Show Region", width=10, command=lambda: self.show_region())
		self.regions_button.grid(row=1,column=5, sticky='n')

		self.regions_button = tk.Button(
			self.frame, text="Show Publish", width=10, command=lambda: self.show_publish())
		self.regions_button.grid(row=1,column=5, sticky='s')

		self.regions_button = tk.Button(
			self.frame, text="Show Request", width=10, command=lambda: self.show_request())
		self.regions_button.grid(row=2,column=5, sticky='s')

		#self.button = tk.Button(
		#	self.frame, text="DDoS", fg="red", width=10, command=lambda: self.DDoS()
		#	)
		#self.button.grid(row=3,column=5, sticky='n')

		self.button = tk.Button(
			self.frame, text="RRT", fg="red", width=10, command=lambda: self.round_trip_time()
			)
		self.button.grid(row=3,column=5, sticky='n')

		#self.button = tk.Button(
		#	self.frame, text="status", fg="red", width=10, command=lambda: self.status()
		#	)
		#self.button.grid(row=3,column=5, sticky='s')

		


		## Enqueue the build into the mainloop
		self.root.after(0, self.build_with_gui(self.levels))
		##
		self.root.after_idle(self.assemble_regions)	
		self.root.wm_title("Name Based Routing Simulator")
		self.frame.update_idletasks()
		self.canvas.config(scrollregion=self.canvas.bbox("all"))
		self.root.after_idle(self.prepare)
		self.root.after_idle(self.animation)
		self.root.mainloop()
		
	



	## Callback funcions for buttons in GUI
	def pressed(self, button): # Updates the display of simulator state 
		self.simulation_state.set(str(button))
		self.frame.update()

	def play(self):
		self.root.after(self.delay,self.animation)
		logging.debug(' Pressed: PLAY')
		self.simulation_state.set('PLAYING')
		#self.frame.update_idletasks()

	def pause(self):
		logging.debug(' Pressed: PAUSE')
		self.simulation_state.set('PAUSED')
		#self.frame.update_idletasks()

	def quit(self):
		self.flag = False
		sys.exit()
		sys.quit()

	def highlight(self):   # Used for debugging to highlight a node or region
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

	def show_region(self):
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

	def show_publish(self):
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

	def request_freq_callback(self, new_value):
		self.request_freq.set(new_value)

	def show_request(self):
		node_id = 2200
		content_name = '10454'
		self.enqueue_to_incoming(node_id, {'content_name': content_name, 'from_id':0, '_type': 'request', 'size': 1})
		color_dict = self.get_color(node_id)
		canvas_id = self.nodes[node_id].canvas_id
		self.canvas.itemconfig(canvas_id, outline=color_dict['color'], width=color_dict['width'])
		#self.canvas.update()
		
	def round_trip_time(self):
		logging.debug('Initializing RTT test:')
		#if method=='random':
		#	logging.debug('Starting random content test:')
		#	pass
		#elif method=='no cache':
		logging.debug('Starting no cached content test:')
		for index in range(0,50):
			name = self.content_names[index]
			requester_id = self.get_random_leaf_machine()
			time_start = time.clock()
			packet = {'content_name':name, '_type':'request', 'from_id':0, 'time_start':time_start, 'size':1 }
			self.enqueue_to_incoming(requester_id, packet )
			logging.debug('Content name: %s -- Requester ID: %d -- Packet %s', name, requester_id, str(packet))

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

	def DDoS_follow_up(self, DDoS_region, content_name):  # Can be called amidst a DDoS to show content is still reachable 
		#selectable_regions = range(0,DDoS_region) + range(DDoS_region+1,len(self.regions))
		#selected_region = random.choice(selectable_regions)
		selected_region = 2
		node_id = self.regions[selected_region][0]
		self.enqueue_to_incoming(node_id, {'content_name': content_name, 'from_id':0, '_type': 'request', 'size': 1} )
		color_dict = self.get_color(node_id)
		self.canvas.itemconfig(self.nodes[node_id].canvas_id, outline=color_dict['color'], width=color_dict['width'])
		
	def update_delay(self, new_value):
		val = new_value[0]
		val = int(val)
		if val == 0:
			self.delay = 100
		else:
			self.delay = val * 1000
		#print self.delay

	def test_nums(self):
		""" Displays whether nodes where numbered correctly """
		for i in range(1,100):
			print i
			self.canvas.itemconfig(self.nodes[i].canvas_id, outline='yellow', width=2.0)
			self.canvas.update_idletasks()
			self.canvas.itemconfig(self.nodes[i].canvas_id, outline='grey', width=1.0)
			self.canvas.update_idletasks()

	def zoom(self, method):  # Used for both zooming in and out
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

	def _zoom(self, level,i,r,x,y):  # Recursive Helper
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
			self.root.after(0, self._zoom(level-1,7*i+1,r/3,x,(y)))

			#north
			color_width = self.get_color(7*i+2)
			canvas_id = self.canvas.create_circle(x, (y-(2.0*r)) , r, outline = color_width['color'], width = color_width['width'])
			self.nodes[7*i+2].canvas_id = canvas_id
			self.root.after(0, self._zoom(level-1,7*i+2,r/3,x,(y-(2.0*r))))

			#south
			color_width = self.get_color(7*i+3)
			canvas_id = self.canvas.create_circle(x, (y+(2.0*r)) , r, outline = color_width['color'], width = color_width['width'])
			self.nodes[7*i+3].canvas_id = canvas_id
			self.root.after(0, self._zoom(level-1,7*i+3,r/3,x,(y+(2.0*r))))

			#northeast
			color_width = self.get_color(7*i+4)
			canvas_id = self.canvas.create_circle(x+2*r*math.sqrt(3)/2, (y-r) , r, outline = color_width['color'], width = color_width['width'])            
			self.nodes[7*i+4].canvas_id = canvas_id
			self.root.after(0, self._zoom(level-1,7*i+4,r/3,x+2*r*math.sqrt(3)/2,(y-r)))

			#southeast
			color_width = self.get_color(7*i+5)
			canvas_id = self.canvas.create_circle(x+2*r*math.sqrt(3)/2, (y+r) , r, outline = color_width['color'], width = color_width['width'])
			self.nodes[7*i+5].canvas_id = canvas_id
			self.root.after(0, self._zoom(level-1,7*i+5,r/3,x+2*r*math.sqrt(3)/2,(y+r)))

			#northwest
			color_width = self.get_color(7*i+6)
			canvas_id = self.canvas.create_circle( x-2*r*math.sqrt(3)/2 , (y-r) , r, outline = color_width['color'], width = color_width['width'])
			self.nodes[7*i+6].canvas_id = canvas_id
			self.root.after(0, self._zoom(level-1,7*i+6,r/3,x-2*r*math.sqrt(3)/2,(y-r)))

			#southwest
			color_width = self.get_color(7*i+7)
			canvas_id = self.canvas.create_circle( x-2*r*math.sqrt(3)/2, (y+r) , r, outline = color_width['color'], width = color_width['width'])
			self.nodes[7*i+7].canvas_id = canvas_id
			self.root.after(0, self._zoom(level-1,7*i+7,r/3,x-2*r*math.sqrt(3)/2,(y+r)))
					
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
		





	## Functionality used for coupling with gui
	def animation(self):
		if self.simulation_state.get() == 'PLAYING':
			self.root.after_idle(self.draw)
			self.step()  # Does a process and deliver
			self.deliver_in_transit_packets()
			self.root.after(self.delay,self.animation)

			#self.root.after(delay,self.aim)

	def draw(self):
		# draw the board according to the current state
		 self.canvas.update_idletasks()
		# arrange for the next frame to draw in 4 seconds
				
	def build_with_gui(self, levels):   # Used for commercial demonstration of the Simulator 
		self._build_with_gui(levels, 0, 150, 600, 540)
	
	def _build_with_gui(self, level,i,r,x,y):  # Recursive helper
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
			self.nodes[7*i+1] = NBRouter(7*i+1, canvas_id, self.gui_boolean)
			self.canvas.create_circle(x, y , r, outline = 'grey', width = 1.0, tags=str(7*i+1))
			self.root.after(0, self._build_with_gui(level-1,7*i+1,r/3,x,(y)))

			#north
			canvas_id = self.canvas.create_circle(x, (y-(2.0*r)) , r, outline = 'grey', width = 1.0, tags=str(7*i+2))
			self.nodes[7*i+2] = NBRouter(7*i+2, canvas_id, self.gui_boolean)
			self.root.after(0, self._build_with_gui(level-1,7*i+2,r/3,x,(y-(2.0*r))))

			#south
			canvas_id = self.canvas.create_circle(x, (y+(2.0*r)) , r, outline = 'grey', width = 1.0, tags=str(7*i+3))
			self.nodes[7*i+3] = NBRouter(7*i+3, canvas_id, self.gui_boolean)
			self.root.after(0, self._build_with_gui(level-1,7*i+3,r/3,x,(y+(2.0*r))))

			#northeast
			canvas_id = self.canvas.create_circle(x+2*r*math.sqrt(3)/2, (y-r) , r, outline = 'grey', width = 1.0, tags=str(7*i+4))            
			self.nodes[7*i+4] = NBRouter(7*i+4, canvas_id, self.gui_boolean)
			self.root.after(0, self._build_with_gui(level-1,7*i+4,r/3,x+2*r*math.sqrt(3)/2,(y-r)))

			#southeast
			canvas_id = self.canvas.create_circle(x+2*r*math.sqrt(3)/2, (y+r) , r, outline = 'grey', width = 1.0, tags=str(7*i+5))
			self.nodes[7*i+5] = NBRouter(7*i+5, canvas_id, self.gui_boolean)
			self.root.after(0, self._build_with_gui(level-1,7*i+5,r/3,x+2*r*math.sqrt(3)/2,(y+r)))

			#northwest
			canvas_id = self.canvas.create_circle( x-2*r*math.sqrt(3)/2 , (y-r) , r, outline = 'grey', width = 1.0, tags=str(7*i+6))
			self.nodes[7*i+6] = NBRouter(7*i+6, canvas_id, self.gui_boolean)
			self.root.after(0, self._build_with_gui(level-1,7*i+6,r/3,x-2*r*math.sqrt(3)/2,(y-r)))

			#southwest
			canvas_id = self.canvas.create_circle( x-2*r*math.sqrt(3)/2, (y+r) , r, outline = 'grey', width = 1.0, tags=str(7*i+7))
			self.nodes[7*i+7] = NBRouter(7*i+7, canvas_id, self.gui_boolean)
			self.root.after(0, self._build_with_gui(level-1,7*i+7,r/3,x-2*r*math.sqrt(3)/2,(y+r)))
					
		else:
			if level == 0:
				#center
				canvas_id = self.canvas.create_circle(x, y , r, outline = 'grey', width = 1.0, tags=str(7*i+1))
				self.nodes[7*i+1] = NBRouter(7*i+1, canvas_id, self.gui_boolean)
				
				#north
				canvas_id = self.canvas.create_circle(x, (y-(2.0*r)) , r, outline = 'grey', width = 1.0, tags=str(7*i+2))
				self.nodes[7*i+2] = NBRouter(7*i+2, canvas_id, self.gui_boolean)
			   
				#south
				canvas_id = self.canvas.create_circle(x, (y+(2.0*r)) , r, outline = 'grey', width = 1.0, tags=str(7*i+3))
				self.nodes[7*i+3] = NBRouter(7*i+3, canvas_id, self.gui_boolean)

				#northeast
				canvas_id = self.canvas.create_circle(x+2*r*math.sqrt(3)/2, (y-r), r, outline = 'grey', width = 1.0, tags=str(7*i+4))
				self.nodes[7*i+4] = NBRouter(7*i+4, canvas_id, self.gui_boolean)
			   
				#southeast
				canvas_id = self.canvas.create_circle(x+2*r*math.sqrt(3)/2, (y+r) , r, outline = 'grey', width = 1.0, tags=str(7*i+5))
				self.nodes[7*i+5] = NBRouter(7*i+5, canvas_id, self.gui_boolean)
			  
				#northwest
				canvas_id = self.canvas.create_circle(x-2*r*math.sqrt(3)/2, (y-r) , r, outline = 'grey', width = 1.0, tags=str(7*i+6))
				self.nodes[7*i+6] = NBRouter(7*i+6, canvas_id, self.gui_boolean)
			   

				#southwest
				canvas_id = self.canvas.create_circle(x-2*r*math.sqrt(3)/2, (y+r) , r, outline = 'grey', width = 1.0, tags=str(7*i+7))
				self.nodes[7*i+7] = NBRouter(7*i+7, canvas_id, self.gui_boolean)

	## Debugging functions
	def in_transit(self): # Used for debugging
		logging.debug(' packets in transit: %s', str(self.in_transit_packets))

	def _create_circle(self, x, y, r, **kwargs):
		"""implementation for creating a circle in Tk"""
		return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
	tk.Canvas.create_circle = _create_circle

	def status(self):
		print str(self.in_transit_packets)
		for n in self.nodes:
			print str(self.nodes[n].incoming)

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
			self.root.after(0,self.deliver_in_transit_packets)      

	def enqueue_to_incoming(self, node_id, packet):
		#self.nodes[node_id].total_load += packet['size']
		self.nodes[node_id].incoming.append(packet)
		color_dict = self.get_color(node_id)
		canvas_id = self.nodes[node_id].canvas_id
		self.canvas.itemconfig(canvas_id, outline=color_dict['color'], width=color_dict['width'])
		self.canvas.itemconfig(self.nodes[self.get_actual_node(node_id)].canvas_id, outline=color_dict['color'], width=color_dict['width'])

	def step(self):
		for n in reversed(range(1, len(self.nodes))):
			self.process(n)       
		#self.deliver_in_transit_packets()

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
				#inself.nodes[node_id].total_load -= packet['size']
				pack = str(packet)
				logging.debug(" packet data: %s", pack) 
				
				#Update the color now that we popped an incoming packet
				""" TODO: UNCOMMENT IF USING GUI"""
				color_dict = self.get_color(node_id)
				self.canvas.itemconfig(self.nodes[node_id].canvas_id, outline=color_dict['color'], width=color_dict['width'])
				self.canvas.itemconfig(self.nodes[self.get_actual_node(node_id)].canvas_id, outline=color_dict['color'], width=color_dict['width'])


				if packet['_type'] == 'request':
					# Packet is a request      
					content_name = packet['content_name']
					requester_id = packet['from_id']  
					time_start = packet['time_start']     
					
					# Case 1: content in cache
					if content_name in self.nodes[node_id].content_store:
						if requester_id == 0:
							logging.debug(" DONE! Content already cached, I am the source: %d" % node_id)
							# Case where active request hasnt been created yet but content in cache
				
						else:
							self.nodes[node_id].outgoing_packet({ 'content_name': content_name, 'from_id':node_id,
																 'content_data':self.nodes[node_id].content_store[content_name], 
																 'dest_id':requester_id, '_type':'response', 'size':1, 'time_start':packet['time_start']},
																 self.in_transit_packets)
							logging.debug(" content %s already in cache", content_name) 
							logging.debug(" sent content back to  %d ", requester_id)
							
					# Case 2: duplicate request exists
					elif content_name in self.nodes[node_id].pending_table:   
						self.nodes[node_id].pending_table[content_name] += [requester_id]
						logging.debug(" duplicate request for content , added requester_id to PT") 
						
					# Case 3: no pending request, but location lives in children, create entry in PT, send request to child
					elif content_name in self.nodes[node_id].forwarding_table:
						directed_child_id  = self.nodes[node_id].forwarding_table[content_name]   #direction of child where destination node is contained 
						self.nodes[node_id].pending_table[content_name] = [requester_id]          # entry in PT created
						self.nodes[node_id].outgoing_packet( {'content_name': content_name , 'dest_id':directed_child_id, 
															  'from_id': node_id, '_type': 'request', 'size':1, 'time_start':packet['time_start']}, self.in_transit_packets)
						logging.debug(" location content %s known, entry for requester %d created in PT", content_name, requester_id) 
						logging.debug(" forwarded request to child %d ", directed_child_id )

					# Case 4: no duplicate, add to PT, forward to parent 
					else:
						self.nodes[node_id].pending_table[content_name] = [requester_id]
						parent_id = self.get_parent(node_id)
						self.nodes[node_id].outgoing_packet({'content_name':content_name, 'from_id':node_id, 'dest_id': parent_id, "_type": 'request', 'size':1, 'time_start':time_start }, self.in_transit_packets)
						logging.debug(" content %s NOT known, entry for requester %d created in PT, sent request,  to parent %d", content_name, requester_id, parent_id) 
						print 'time start is' + str(packet['time_start'])
					  	



				elif packet['_type'] == 'response':
					# packet is a response
					content_name = packet['content_name']
					data = packet['content_data'] 

					# Case 1: node is source of request, 0 signifies it is the source of request
					if ((0 in self.nodes[node_id].pending_table[content_name]) and (len(self.nodes[node_id].pending_table[content_name])==1)):
						print packet['time_start']
						time_now = time.clock()
						self.round_trip_times.append(float(time_now - packet['time_start']))
						#nowself.root.after_idle(self.single_RRT_average)
						logging.debug(" DONE! I am the source: %d" % node_id)
						self.nodes[node_id].content_store[content_name] = data
						logging.debug(" Added content (%s) to content store"  % content_name)
						del self.nodes[node_id].pending_table[content_name]
						logging.debug(" Deleted content (%s) from PT"  % content_name)
						# Remove from the networks active requests monitor
						
					# Case 2: node was a middle man
					else:
						print logging.debug("Forwarding response along to all requesters, I am: %d ... ", node_id)
						for dest_id in self.nodes[node_id].pending_table[content_name]:
							if dest_id == 0:
								logging.debug(" DONE! I am a source: %d" % node_id)
							else:
								self.nodes[node_id].outgoing_packet({'content_name':packet['content_name'], 'from_id':node_id, 
																	 'content_data':data, '_type':'response', 'dest_id':dest_id, 'size':1,
																	 'time_start':packet['time_start']},
																	self.in_transit_packets )
								logging.debug("Sent response to requester %d ", dest_id)
								logging.debug("Forwarding to all requesters complete")

						del self.nodes[node_id].pending_table[content_name]
						logging.debug(" Deleted content (%s) from PT"  % content_name)
						self.nodes[node_id].content_store[packet['content_name']] = data
						logging.debug(" Added content (%s) to content store"  % content_name)

					""" TODO: UNCOMMENT IF USING GUI """
					color_dict = self.get_color(node_id)
					self.canvas.itemconfig(self.nodes[node_id].canvas_id, outline=color_dict['color'], width=color_dict['width'])
					self.canvas.itemconfig(self.nodes[self.get_actual_node(node_id)].canvas_id, outline=color_dict['color'], width=color_dict['width'])
					
				else:
					logging.warning(' Mislabeled Packet')
					""" TODO: UNCOMMENT IF USING GUI """
					color_dict = self.get_color(node_id)
					self.canvas.itemconfig(self.nodes[node_id].canvas_id, outline=color_dict['color'], width=color_dict['width'])
					self.canvas.itemconfig(self.nodes[self.get_actual_node(node_id)].canvas_id, outline=color_dict['color'], width=color_dict['width'])
					
			i += 1









	## Core simulator functions				
	def build_without_gui(self, levels):   # Used for commercial demonstration of the Simulator 
		self._build_without_gui(levels, 0)
	
	def _build_without_gui(self, level,i):  # Recursive helper
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
			self.nodes[7*i+1] = Routers.NBRouter(7*i+1, 0, self.gui_boolean)
			self._build_without_gui(level-1,7*i+1,)

			#north
			self.nodes[7*i+2] = Routers.NBRouter(7*i+2, 0, self.gui_boolean)
			self._build_without_gui(level-1,7*i+2)

			#south
			self.nodes[7*i+3] = Routers.NBRouter(7*i+3, 0, self.gui_boolean)
			self._build_without_gui(level-1,7*i+3)

			#northeast
			self.nodes[7*i+4] = Routers.NBRouter(7*i+4, 0, self.gui_boolean)
			self._build_without_gui(level-1,7*i+4)

			#southeast
			self.nodes[7*i+5] = Routers.NBRouter(7*i+5, 0, self.gui_boolean)
			self._build_without_gui(level-1,7*i+5)

			#northwest
			self.nodes[7*i+6] = Routers.NBRouter(7*i+6, 0, self.gui_boolean)
			self._build_without_gui(level-1,7*i+6)

			#southwest
			self.nodes[7*i+7] = Routers.NBRouter(7*i+7, 0, self.gui_boolean)
			self._build_without_gui(level-1,7*i+7)
					
		else:
			if level == 0:
				#center
				self.nodes[7*i+1] = Routers.NBRouter(7*i+1, 0, self.gui_boolean)
				
				#north
				self.nodes[7*i+2] = Routers.NBRouter(7*i+2, 0, self.gui_boolean)
			   
				#south
				self.nodes[7*i+3] = Routers.NBRouter(7*i+3, 0, self.gui_boolean)

				#northeast
				self.nodes[7*i+4] = Routers.NBRouter(7*i+4, 0, self.gui_boolean)
			   
				#southeast
				self.nodes[7*i+5] = Routers.NBRouter(7*i+5, 0, self.gui_boolean)
			  
				#northwest
				self.nodes[7*i+6] = Routers.NBRouter(7*i+6, 0, self.gui_boolean)
			   

				#southwest
				self.nodes[7*i+7] = Routers.NBRouter(7*i+7, 0, self.gui_boolean)

	def prepare(self):
		content_index = 10000
		## HARD CODED -> 1 object per leaf -> 2458 content objects
		leaf_id = 2790
		while (leaf_id > 450 and self.flag):
			content_name = str(content_index)
			self.publish_content(content_name, content_name, leaf_id)
			self.content_names.append(content_name)
			content_index +=1
			leaf_id -= 5
		logging.debug('  Publishing complete. avail content_names are %d through %d ', int(self.content_names[0]), 
			int(self.content_names[(len(self.content_names) -1)]))
		#self.simulation_state.set("PLAYING")
		#self.frame.update_idletasks()
				
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

	def assemble_regions(self):
		node_id = self.lower_lim
		while node_id in range(self.lower_lim,self.upper_lim):
			region = []
			for i in range(0,7):
				region.append(node_id)
				node_id += 1
			self.regions.append(region)

	def computation_power(self, node_id):
		if node_id <= 7:
			return 4
		elif node_id <= 56:
			return 3
		elif node_id <= 399:
			return 2
		else: 
			return 1
			
	def loop_step(self):
		for n in range(1, len(self.nodes)):
			self.process_without_gui(n) 

		congestion = 0 
		node_level = 0
		for n in range(1, 8):
			congestion +=  len(self.nodes[n].incoming)
		self.level_congestion[node_level] = congestion

		congestion = 0 
		node_level = 1
		for n in range(8, 57):
			congestion +=  len(self.nodes[n].incoming)
		self.level_congestion[node_level] = congestion

		congestion = 0 
		node_level = 2
		for n in range(57, 400):
			congestion +=  len(self.nodes[n].incoming)
		self.level_congestion[node_level] = congestion

		congestion = 0 
		node_level = 3
		for n in range(400, 2801):
			congestion +=  len(self.nodes[n].incoming)
		self.level_congestion[node_level] = congestion

	def process_without_gui(self, node_id):
		# higher level nodes have a faster computation model
		comp_power = self.computation_power(node_id)
		i = 0 
		while i < comp_power:
			# add time of computation to packet lifetime
			#t1 = time.time()

			if (not is_empty(self.nodes[node_id].incoming)):
				logging.debug(' processing incoming packet at %d' % node_id)
				packet = self.nodes[node_id].incoming.popleft()
				logging.debug(" packet data: %s", str(packet)) 


				if packet.type == 'request':   
					  
					# Case 1: content in cache
					if packet.content_name in self.nodes[node_id].content_store:

						if packet.requester_id == 0: # Case where active request hasnt been created yet but content in cache
							logging.debug(" DONE! Content already cached, I am the source: %d" % node_id)
							packet.lifetime += 20
							self.rtt_slices.append(packet.lifetime)
						else:
							self.send_packet('response', packet.content_name,  node_id, packet.requester_id, packet.lifetime, self.nodes[node_id].content_store[packet.content_name])
							logging.debug(" content %s already in cache", packet.content_name) 
							logging.debug(" sent content back to  %d ", packet.requester_id)
							
					# Case 2: duplicate request exists
					elif packet.content_name in self.nodes[node_id].pending_table:   

						self.nodes[node_id].pending_table[packet.content_name] += [packet.requester_id]
						#logging.debug(" duplicate request for content %s , added requester_id %d to PT", packet[content_name], packet[requester_id]) 
						logging.debug(" duplicate request for content , added requester_id %d to PT", packet.requester_id) 
					
						
					# Case 3: no pending request, but location lives in children, create entry in PT, send request to child
					elif packet.content_name in self.nodes[node_id].forwarding_table:

						directed_child_id  = self.nodes[node_id].forwarding_table[packet.content_name]   #direction of child where destination node is contained 
						self.nodes[node_id].pending_table[packet.content_name] = [packet.requester_id]          # entry in PT created
						self.send_packet( 'request', packet.content_name ,node_id, directed_child_id, packet.lifetime)
						logging.debug(" location content %s known, entry for requester %d created in PT", packet.content_name, packet.requester_id) 
						logging.debug(" forwarded request to child %d ", directed_child_id )

					# Case 4: no duplicate, add to PT, forward to parent 
					else:
						self.nodes[node_id].pending_table[packet.content_name] = [packet.requester_id]
						parent_id = self.get_parent(node_id)
						self.send_packet('request', packet.content_name, node_id, parent_id, packet.lifetime )
						logging.debug(" content %s NOT known, entry for requester %d created in PT, sent request,  to parent %d", packet.content_name, packet.requester_id, parent_id) 
					 

				elif packet.type == 'response':
					# packet is a response

					# Case 1: node is source of request, 0 signifies it is the source of request
					if ((0 in self.nodes[node_id].pending_table[packet.content_name]) and (len(self.nodes[node_id].pending_table[packet.content_name])==1)):
						self.rtt_slices.append(packet.lifetime)
						logging.debug(" DONE! I am the source: %d" % node_id)
						self.nodes[node_id].content_store[packet.content_name] = packet.content_data
						logging.debug(" Added content (%s) to content store"  % packet.content_name)
						del self.nodes[node_id].pending_table[packet.content_name]
						logging.debug(" Deleted content (%s) from PT"  % packet.content_name)
						# Remove from the networks active requests monitor
						
					# Case 2: node was a middle man
					else:
						print logging.debug("Forwarding response along to all requesters, I am: %d ... ", node_id)
						for dest_id in self.nodes[node_id].pending_table[packet.content_name]:
							if dest_id == 0:
								logging.debug(" DONE! I am a source: %d" % node_id)
							else:
								self.send_packet('response', packet.content_name, node_id, dest_id, packet.lifetime, packet.content_data) 			
								logging.debug("Sent response to requester %d ", dest_id)
						logging.debug("Forwarding to all requesters complete")

						del self.nodes[node_id].pending_table[packet.content_name]
						logging.debug(" Deleted content (%s) from PT"  % packet.content_name)
						self.nodes[node_id].content_store[packet.content_name] = packet.content_data
						logging.debug(" Added content (%s) to content store"  % packet.content_name)

				
					
				else:
					logging.warning(' Mislabeled Packet')
					
			i += 1

	def send_packet(self, _type, content_name, from_id, dest_id, lifetime, *args):
		if args:
			pack = Packet(_type, content_name, from_id,  dest_id, args[0])
		else:
			pack = Packet(_type, content_name, from_id,  dest_id)
		if pack:
			pack.lifetime += (20 + lifetime) # Latency in delivering a packet
		if self:
			self.packets_to_be_delivered.append(pack)

	def deliver_packets(self):
		if not is_empty(self.packets_to_be_delivered):
			pack = self.packets_to_be_delivered.pop()
			dest_id = pack.dest_id
			self.nodes[dest_id].incoming.append(pack)
			self.deliver_packets()
		else:
			congestion = 0 
			node_level = 0
			for n in range(1, 8):
				congestion +=  len(self.nodes[n].incoming)
			self.level_congestion[node_level] = congestion

			congestion = 0 
			node_level = 1
			for n in range(8, 57):
				congestion +=  len(self.nodes[n].incoming)
			self.level_congestion[node_level] = congestion

			congestion = 0 
			node_level = 2
			for n in range(57, 400):
				congestion +=  len(self.nodes[n].incoming)
			self.level_congestion[node_level] = congestion

			congestion = 0 
			node_level = 3
			for n in range(400, 2801):
				congestion +=  len(self.nodes[n].incoming)
			self.level_congestion[node_level] = congestion	

	def packet_generator(self,size):
		for i in range(0,size):
			content_name = self.content_names[random.randint(0,len(self.content_names)-1)]
			requester_id = self.get_random_leaf_machine()
			self.send_packet('request',content_name,0,requester_id,0)
	
	def warm_up(self,warm_up_seconds):
		self.packet_generator(50)
		start = time.time()
		end = time.time()
		while end-start <= warm_up_seconds:
			self.deliver_packets()
			self.loop_step()
			self.packet_generator(5)
			end=time.time()
		self.simulator(25)


	def simulator(self, seconds):
		sched = Scheduler(daemon=True)
		sched.start()
		sched.add_interval_job(self.log_level_congestion, seconds=2)
		duration_seconds = seconds
		start = time.time()
		end = time.time()
		print 'start'
		while end-start <= duration_seconds:
			self.deliver_packets()
			sys.stdout.write('.')
			self.loop_step()
			end = time.time()
			self.packet_generator(50)
		self.write_level_congestions()
		sched.shutdown()

	def log_level_congestion(self):
		self.total_congestions.append(copy.deepcopy(self.level_congestion))

	def write_level_congestions(self):
		for dic in self.total_congestions:
			for key, value in dic.iteritems():
				open("level_congestion.csv","a").write(str(value)+ ',')
			open("level_congestion.csv","a").write("'\n'")

	def write_average_rtt(self):
		for item in self.rtt_slices:
			open("rtt.csv","a").write(str(item) + ' ')





	## Utility functions for network accessability 

	def get_other_leaf_machine(self,node_id):
		x = node_id
		while x == node_id:
			x = random.randint(self.lower_lim, self.upper_lim)
		return x

	def get_random_leaf_machine(self):
		return random.randint(self.lower_lim+1, self.upper_lim)
	
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
		size = self.nodes[node_id].total_load()
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
			elif size < 10:
				return {'color':'blue', 'width':2.0}
			elif size < 75:
				return {'color':'dark orange', 'width':2.0}
			elif size < 101:
				return {'color':'red', 'width':2.0}
			else: 
				return {'color':'red', 'width':2.0}
	
	
		

	
		

##
# End of Program
##