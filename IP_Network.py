##
# IP Network implementation
# 
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
from multiprocessing import Pool

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


def set_tick_ds(levels):
	dictionary = {}
	for i in range(0,levels+1):
		dictionary[i] = []
	return dictionary

def set_congestion_ds(levels):
	dictionary = {}
	for i in range(0,levels+1):
		dictionary[i] = 0
	return dictionary

def set_lower_lim(levels):
	total = 0 
	for i in range(0,levels):
		total += (7**i)
	return total

def set_upper_lim(levels):
	total = 0 
	for i in range(0,levels+1):
		total += (7**i)
	return total - 1


def set_level_ranges(levels, upper_lim):
	dictionary={}
	dictionary[0] = [0]
	total = 0


	for i in range(1,levels+1):
		old_total = total +1
		total += 7**i
		dictionary[i] = [old_total, total]
	
	node_dict = {}
	node_dict[0] = 0
	for node_id in range(1, upper_lim + 1):
		for i in range(1, levels+1):
			if node_id >= dictionary[i][0] and node_id <= dictionary[i][1]:
				node_dict[node_id] = i

	return node_dict


def set_computation_ds(levels):
	dictionary = {}
	power = -4
	for i in reversed(range(0,levels+1)):
		power += 5
		dictionary[i] = power
	return dictionary

def set_cache_ds(levels):
	dictionary = {}
	slots = 20
	for i in reversed(range(0,levels+1)):
		#slots += 20
		dictionary[i] = slots
	return dictionary

class IP_Network(object):
	def __init__( self, levels, gui_boolean, p=.2, q=.2 ):
		
		# data structs for the network, core data structures
		self.nodes = {}
		self.levels = levels
		self.lower_lim = set_lower_lim(levels)
		self.upper_lim = set_upper_lim(levels)
		self.content_names = []
		self.regions = []
		self.level_ranges_dict = set_level_ranges(levels, self.upper_lim) 

		self.level_congestion = set_congestion_ds(levels)
		self.total_congestions = []
		self.packets_to_be_delivered = []
		self.ip_rt_tick_times = []
		self.ip_rt_tick_means = []
		self.packets_delivered_count = 0 
		self.packets_delivered_slices = []
		self.rt_ticks_by_level = set_tick_ds(levels)
		self.total_rt_by_levels = []
		self.computation_power = set_computation_ds(levels)
		self.cache_slots = set_cache_ds(levels)
		self.packet_gen_job = None 
		self.p = p    # probability of request arising at a node
		self.q = q    # probability of node being chosen to publish content


		self.gui_boolean = gui_boolean
		if self.gui_boolean:
			self.x_origin = 900
			self.y_origin = 540
			self.radius = 150 
			self.flag = True
			self.in_transit_packets = []
			self.delay = 500
			self.ammo = 0 
			self.simulation_state = ''
			self.root = ''
			self.radius = 150
			self.zoom_level = 0
			self.initialize_gui()
			self.command_entry = ''
		else:
			self.packet_frequency = int((7**self.levels) * self.p)
			self.sched = Scheduler(daemon=True)
			self.build_without_gui(self.levels)
		self.prepare()
		self.assemble_regions()
		self.set_up_cache()
		
	## Buttons and Sliders
	def initialize_gui(self):
		self.root = tk.Tk()
		self.simulation_state = tk.StringVar()
		self.simulation_state.set('PLAYING')
		self.command_entry = tk.StringVar()

		# Give the window scrolls
		vscrollbar = AutoScrollbar(self.root)
		vscrollbar.grid(row=0, column=3, sticky='n'+'s')
		hscrollbar = AutoScrollbar(self.root, orient='horizontal')
		hscrollbar.grid(row=2, column=0, sticky='e'+'w')

		self.frame = tk.Frame(self.root, height=500,width=1000, relief='raised', bd=2)
		self.frame.grid(row=0,column=0)
		self.frame.grid_rowconfigure(0, weight=0)
		self.frame.grid_columnconfigure(0, weight=1)

		self.canvas = tk.Canvas(self.root,width=825,height=600,
                yscrollcommand=vscrollbar.set,
                xscrollcommand=hscrollbar.set)
		self.canvas.grid(row=1, column=0, sticky='e'+'w'+'n'+'s', columnspan=2)
		self.canvas.grid_columnconfigure(0, weight=1)
		self.canvas.grid_rowconfigure(1, weight=1)

		vscrollbar.config(command=self.canvas.yview)
		hscrollbar.config(command=self.canvas.xview)

		# make the frame not expandable
		self.root.grid_rowconfigure(0, weight=0, minsize=0)
		self.root.grid_columnconfigure(0, weight=0, minsize=700)
		# make the canvas expandable
		self.root.grid_rowconfigure(1, weight=1, minsize=150)
		self.root.grid_columnconfigure(0, weight=1, minsize=700)
		

		# heatmap image 
		photo = tk.PhotoImage(file="heat1.gif")
		self.label = tk.Label(
			self.frame, text="Machine Load", image=photo, anchor='w', justify='left', compound=tk.BOTTOM)
		self.label.photo = photo
		self.label.grid(row=0,column=7, columnspan=4)

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
		self.request_freq.grid(row=0,column=1)

		self.button = tk.Button(
			self.frame, text="PLAY", fg="red", command=lambda: self.play()
			)
		self.button.grid(row=0,column=2)

		self.button = tk.Button(
			self.frame, text="PAUSE", fg="red", command=lambda: self.pause()
			)
		self.button.grid(row=0,column=3)		####

		#self.set_buttons()
		self.button = tk.Button(
			self.frame, text="QUIT", fg="red", command=lambda: self.quit()
			)
		self.button.grid(row=0,column=4)

		# zoom in
		self.zoom_button = tk.Button(
			self.frame, text="ZOOM +", command=lambda: self.zoom('in'))
		self.zoom_button.grid(row=0,column=5, sticky='n')

		# zoom out 
		self.zoom_button = tk.Button(
			self.frame, text="ZOOM -", command=lambda: self.zoom('out'))
		self.zoom_button.grid(row=0,column=5, sticky='s')
		
		self.entry1 = tk.Entry(
			self.frame, textvariable=self.command_entry)
		self.entry1.insert(0, "Enter Command")
		self.entry1.grid(row=0,column=6, sticky='n')

		self.highlight_button = tk.Button(
			self.frame, text="Enter", width=10, command=lambda: self.command_line())
		self.highlight_button.grid(row=0,column=6,sticky='s')
		


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
		
	




	## Callback funcions for Buttons in GUI
 	def pressed(self, button):  # Updates the display of simulator state 
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

	def command_line(self):
		args = str(self.command_entry.get()).split(' ')
		args[0] = args[0].lower()
		if args[0] == 'highlight':
			node_id = int(args[1])
			self.highlight(node_id)
		elif args[0] == 'publish':
			self.show_publish()
		elif args[0] == 'request':
			self.show_request()
		elif args[0] == 'ddos':
			self.DDoS()
		else:
			logging.debug("Invalid Command %s --- Options are: \n highlight {node id} \n publish \n request \n DDoS", str(self.command_entry.get()))

	def highlight(self,node_id):   # Used for debugging to highlight a node or region
		""" Used for highlighting a single node """
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


	def show_publish(self):
		source_id = 1000
		content_name = 'espn.com/usa-world-cup-winner'
		if self.delay > 500:
			self.canvas.itemconfig(self.nodes[source_id].canvas_id, outline='purple', width=2.0)
			self.canvas.update()
			sleep(self.delay/1000)
			self.canvas.itemconfig(self.nodes[source_id].canvas_id, outline='grey', width=1.0)
			self.canvas.update()
		
		# Get all parents of source node until reaching root 0
		current = source_id
		parent_id = self.get_parent(source_id)
		while ( parent_id != -1 ):    # parent of 1 always returns -1
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
		self.enqueue_to_incoming(node_id, {'content_name': content_name, 'from_id':-1, '_type': 'request', 'size': 1})
		color_dict = self.get_color(node_id)
		canvas_id = self.nodes[node_id].canvas_id
		self.canvas.itemconfig(canvas_id, outline=color_dict['color'], width=color_dict['width'])
		self.canvas.update()

	def DDoS(self):
		DDoS_region = self.regions[random.randint(0,len(self.regions)-1)]
		content_name = self.content_names[random.randint(0,len(self.content_names)-1)]
		self._DDoS(DDoS_region, content_name, self.ammo)
		#self.root.after(10000, self.DDoS_follow_up, DDoS_region, content_name)
	
	def _DDoS(self, region_nodes,content_name, size ):
		node_id = region_nodes[random.randint(1,6)]
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
		
	def update_delay(self, new_value):
		val = new_value[0]
		val = int(val)
		if val == 0:
			self.delay = 100
		else:
			self.delay = val * 1000

	def zoom(self, method):  # Used for both zooming in and out
		if method == 'in':
			self.radius *= 1.2
			self.zoom_level += 1
		else:
			self.radius *= .8
			self.zoom_level -= 1
		self.pause()
		self.canvas.delete('all')

		color_width = self.get_color(0)
		canvas_id = self.canvas.create_circle(self.x_origin, self.y_origin , self.radius*3, outline = color_width['color'], width = color_width['width'])
		self.nodes[0].canvas_id = canvas_id
		self._zoom(self.levels, 0, self.radius, self.x_origin, self.y_origin)
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
		





	## Simulator Functionality for GUI
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
		canvas_id = self.canvas.create_circle(self.x_origin, self.y_origin , self.radius*3, outline = 'grey', width = 1.0)
		self.nodes[0] = IPRouter(0, canvas_id, self.gui_boolean)
		self._build_with_gui(levels-1, 0, self.radius, self.x_origin, self.y_origin)
	
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
			canvas_id = self.canvas.create_circle(x, y , r, outline = 'grey', width = 1.0)
			self.nodes[7*i+1] = IPRouter(7*i+1, canvas_id, self.gui_boolean)
			self.canvas.create_circle(x, y , r, outline = 'grey', width = 1.0, tags=str(7*i+1))
			self.root.after(0, self._build_with_gui(level-1,7*i+1,r/3,x,(y)))

			#north
			canvas_id = self.canvas.create_circle(x, (y-(2.0*r)) , r, outline = 'grey', width = 1.0)
			self.nodes[7*i+2] = IPRouter(7*i+2, canvas_id, self.gui_boolean)
			self.root.after(0, self._build_with_gui(level-1,7*i+2,r/3,x,(y-(2.0*r))))

			#south
			canvas_id = self.canvas.create_circle(x, (y+(2.0*r)) , r, outline = 'grey', width = 1.0)
			self.nodes[7*i+3] = IPRouter(7*i+3, canvas_id, self.gui_boolean)
			self.root.after(0, self._build_with_gui(level-1,7*i+3,r/3,x,(y+(2.0*r))))

			#northeast
			canvas_id = self.canvas.create_circle(x+2*r*math.sqrt(3)/2, (y-r) , r, outline = 'grey', width = 1.0)            
			self.nodes[7*i+4] = IPRouter(7*i+4, canvas_id, self.gui_boolean)
			self.root.after(0, self._build_with_gui(level-1,7*i+4,r/3,x+2*r*math.sqrt(3)/2,(y-r)))

			#southeast
			canvas_id = self.canvas.create_circle(x+2*r*math.sqrt(3)/2, (y+r) , r, outline = 'grey', width = 1.0)
			self.nodes[7*i+5] = IPRouter(7*i+5, canvas_id, self.gui_boolean)
			self.root.after(0, self._build_with_gui(level-1,7*i+5,r/3,x+2*r*math.sqrt(3)/2,(y+r)))

			#northwest
			canvas_id = self.canvas.create_circle( x-2*r*math.sqrt(3)/2 , (y-r) , r, outline = 'grey', width = 1.0)
			self.nodes[7*i+6] = IPRouter(7*i+6, canvas_id, self.gui_boolean)
			self.root.after(0, self._build_with_gui(level-1,7*i+6,r/3,x-2*r*math.sqrt(3)/2,(y-r)))

			#southwest
			canvas_id = self.canvas.create_circle( x-2*r*math.sqrt(3)/2, (y+r) , r, outline = 'grey', width = 1.0)
			self.nodes[7*i+7] = IPRouter(7*i+7, canvas_id, self.gui_boolean)
			self.root.after(0, self._build_with_gui(level-1,7*i+7,r/3,x-2*r*math.sqrt(3)/2,(y+r)))
					
		else:
			if level == 0:
				#center
				canvas_id = self.canvas.create_circle(x, y , r, outline = 'grey', width = 1.0)
				self.nodes[7*i+1] = IPRouter(7*i+1, canvas_id, self.gui_boolean)
				
				#north
				canvas_id = self.canvas.create_circle(x, (y-(2.0*r)) , r, outline = 'grey', width = 1.0)
				self.nodes[7*i+2] = IPRouter(7*i+2, canvas_id, self.gui_boolean)
			   
				#south
				canvas_id = self.canvas.create_circle(x, (y+(2.0*r)) , r, outline = 'grey', width = 1.0)
				self.nodes[7*i+3] = IPRouter(7*i+3, canvas_id, self.gui_boolean)

				#northeast
				canvas_id = self.canvas.create_circle(x+2*r*math.sqrt(3)/2, (y-r), r, outline = 'grey', width = 1.0)
				self.nodes[7*i+4] = IPRouter(7*i+4, canvas_id, self.gui_boolean)
			   
				#southeast
				canvas_id = self.canvas.create_circle(x+2*r*math.sqrt(3)/2, (y+r) , r, outline = 'grey', width = 1.0)
				self.nodes[7*i+5] = IPRouter(7*i+5, canvas_id, self.gui_boolean)
			  
				#northwest
				canvas_id = self.canvas.create_circle(x-2*r*math.sqrt(3)/2, (y-r) , r, outline = 'grey', width = 1.0)
				self.nodes[7*i+6] = IPRouter(7*i+6, canvas_id, self.gui_boolean)
			   

				#southwest
				canvas_id = self.canvas.create_circle(x-2*r*math.sqrt(3)/2, (y+r) , r, outline = 'grey', width = 1.0)
				self.nodes[7*i+7] = IPRouter(7*i+7, canvas_id, self.gui_boolean)

	def _create_circle(self, x, y, r, **kwargs):
		"""implementation for creating a circle in Tk"""
		return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
	tk.Canvas.create_circle = _create_circle

	def deliver_in_transit_packets(self):
		if( not is_empty(self.in_transit_packets)):
			packet = self.in_transit_packets.pop()
			dest_id = packet['dest_id']
			if dest_id == -1 :
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
		for n in reversed(range(0, len(self.nodes))):
			self.process(n)       
		#self.deliver_in_transit_packets()

	def process(self, node_id):
		global process_start_time, process_end_time
		# higher level nodes have a faster computation model
		comp_power = self.get_computation_power(node_id)
		i = 0 
		while i < comp_power:
			# add time of computation to packet lifetime
			#t1 = time.time()

			if (not is_empty(self.nodes[node_id].incoming)):
				logging.debug(' processing incoming packet at %d' % node_id)
				packet = self.nodes[node_id].incoming.popleft()
				logging.debug(" packet data: %s", str(packet)) 
				process_start_time = time.time()


				#Update the color now that we popped an incoming packet
				""" TODO: UNCOMMENT IF USING GUI"""
				color_dict = self.get_color(node_id)
				self.canvas.itemconfig(self.nodes[node_id].canvas_id, outline=color_dict['color'], width=color_dict['width'])
				self.canvas.itemconfig(self.nodes[self.get_actual_node(node_id)].canvas_id, outline=color_dict['color'], width=color_dict['width'])



				if packet.type == 'request':   
					  
					# Case 1: content in cache
					if packet.content_name in self.nodes[node_id].content_store:

						if packet.origin_id == node_id: # I am the source
						# Case where active request hasnt been created yet but content in cache
							logging.debug(" DONE! Content already cached, I am the source: %d" % node_id)
							packet.lifetime += 20
							self.rt_times.append(packet.lifetime)
							self.packets_delivered_count += 1
						else:
							self.send_packet(packet.id, 'response', packet.content_name,  node_id, packet.origin_id, packet.lifetime, self.nodes[node_id].content_store[packet.content_name])
							logging.debug(" content %s already in cache", packet.content_name) 
							logging.debug(" sent content back to  %d ", packet.origin_id)
							

					# Case 2: location of content lives in children, forward request to child
					elif packet.content_name in self.nodes[node_id].forwarding_table:

						directed_child_id  = self.nodes[node_id].forwarding_table[packet.content_name]   #direction of child where destination node is contained 
						self.send_packet( packet.id,'request', packet.content_name ,node_id, directed_child_id, packet.lifetime)
						logging.debug(" forwarded request to child %d ", directed_child_id )

					# Case 3: location of content not known, send to parent
					else:
						parent_id = self.get_parent(node_id)
						self.send_packet(packet.id, 'request', packet.content_name, node_id, parent_id, packet.lifetime )
						logging.debug(" content %s NOT known sent request to parent %d", packet.content_name, packet.origin_id, parent_id)


				elif packet.type == 'response':
					# packet is a response

					# Case 1: node is source of request
					if (node_id == packet.origin_id):
						self.ip_rt_times.append(packet.lifetime)
						self.packets_delivered_count += 1
						logging.debug(" DONE! I am the source: %d" % node_id)
						self.nodes[node_id].cache_content(packet.content_name, packet.content_data)
						logging.debug(" Added content (%s) to content store"  % packet.content_name)
						
					# Case 2: node was a middle man
					else:
						print logging.debug("Forwarding response along to requesters, I am: %d ... ", node_id)
						
						self.send_packet(packet.id, 'response', packet.content_name, node_id, packet.dest_id, packet.lifetime, packet.content_data) 			
						logging.debug("Sent response to requester %d ", packet.dest_id)
						logging.debug("Forwarding to requester complete")

						self.nodes[node_id].cache_content(packet.content_name, packet.content_data)
						logging.debug(" Added content (%s) to content store"  % packet.content_name)

				
					
				else:
					logging.warning(' Mislabeled Packet')

				color_dict = self.get_color(node_id)
				self.canvas.itemconfig(self.nodes[node_id].canvas_id, outline=color_dict['color'], width=color_dict['width'])
				self.canvas.itemconfig(self.nodes[self.get_actual_node(node_id)].canvas_id, outline=color_dict['color'], width=color_dict['width'])

				process_end_time = time.time()
				total_processing_time = (process_end_time - process_start_time)/comp_power
				for packet in self.nodes[node_id].incoming:
					packet.lifetime += total_processing_time
			i += 1
		






	## Functionality for DES			
	def build_without_gui(self, levels):   # Used for commercial demonstration of the Simulator 
		self.nodes[0] = IPRouter(0, 0, self.gui_boolean)
		self._build_without_gui(levels-1, 0)

	
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
			self.nodes[7*i+1] = Routers.IPRouter(7*i+1, 0, self.gui_boolean) # 0 signifies no canvas id
			self._build_without_gui(level-1,7*i+1,)

			#north
			self.nodes[7*i+2] = Routers.IPRouter(7*i+2, 0, self.gui_boolean)
			self._build_without_gui(level-1,7*i+2)

			#south
			self.nodes[7*i+3] = Routers.IPRouter(7*i+3, 0, self.gui_boolean)
			self._build_without_gui(level-1,7*i+3)

			#northeast
			self.nodes[7*i+4] = Routers.IPRouter(7*i+4, 0, self.gui_boolean)
			self._build_without_gui(level-1,7*i+4)

			#southeast
			self.nodes[7*i+5] = Routers.IPRouter(7*i+5, 0, self.gui_boolean)
			self._build_without_gui(level-1,7*i+5)

			#northwest
			self.nodes[7*i+6] = Routers.IPRouter(7*i+6, 0, self.gui_boolean)
			self._build_without_gui(level-1,7*i+6)

			#southwest
			self.nodes[7*i+7] = Routers.IPRouter(7*i+7, 0, self.gui_boolean)
			self._build_without_gui(level-1,7*i+7)
					
		else:
			if level == 0:
				#center
				self.nodes[7*i+1] = Routers.IPRouter(7*i+1, 0, self.gui_boolean)
				
				#north
				self.nodes[7*i+2] = Routers.IPRouter(7*i+2, 0, self.gui_boolean)
			   
				#south
				self.nodes[7*i+3] = Routers.IPRouter(7*i+3, 0, self.gui_boolean)

				#northeast
				self.nodes[7*i+4] = Routers.IPRouter(7*i+4, 0, self.gui_boolean)
			   
				#southeast
				self.nodes[7*i+5] = Routers.IPRouter(7*i+5, 0, self.gui_boolean)
			  
				#northwest
				self.nodes[7*i+6] = Routers.IPRouter(7*i+6, 0, self.gui_boolean)
			   

				#southwest
				self.nodes[7*i+7] = Routers.IPRouter(7*i+7, 0, self.gui_boolean)

	def prepare(self):
		content_index = 10000
		node_count = 7**self.levels
		content_count = node_count * self.q 
		i = 0
		while ( i < content_count):
			leaf_id = random.randint(self.lower_lim, self.upper_lim)
			content_name = str(content_index)
			self.publish_content(content_name, content_name, leaf_id)
			self.content_names.append(content_name)
			content_index +=1
			i += 1
		logging.debug('  Publishing complete. avail content_names are %d through %d ', int(self.content_names[0]), 
			int(self.content_names[(len(self.content_names) -1)]))
		#self.simulation_state.set("PLAYING")
		#self.frame.update_idletasks()
				
	# Helper function for prepare()
	def publish_content( self,content_name, content_data, source_id):
		self.nodes[source_id].content_store[content_name] =  content_data
		
		# Update all parents hash of source node until reaching root 0
		current = source_id
		parent_id = self.get_parent(source_id)
		while ( parent_id != -1 ):    # get_parent of 0 always returns -1
			self.nodes[parent_id].forwarding_table[content_name] = current
			current = parent_id
			parent_id = self.get_parent(parent_id)
		#logging.debug(' Completed updating FT of parents of %d ' % dest_id)

	def assemble_regions(self):
		node_id = self.lower_lim
		region_num = 1 
		while node_id in range(node_id,self.upper_lim):
			region = []
			for i in range(0,7):
				region.append(node_id)
				self.nodes[node_id].region_num = region_num
				self.update_region(node_id, region_num)
				node_id += 1
			region_num += 1
			self.regions.append(region)

	def update_region(self, source_id, region_num):
		# Update all parents hash of node n's region
		current = source_id
		parent_id = self.get_parent(source_id)
		while ( parent_id != -1 ):    # get_parent of 0 always returns -1
			if region_num not in self.nodes[parent_id].contained_regions:
				self.nodes[parent_id].contained_regions[region_num] = True
			current = parent_id
			parent_id = self.get_parent(parent_id)
		#logging.debug(' Completed updating FT of parents of %d ' % dest_id)

	def test_regionality_topdown(self):
		for leaf_id in range(self.lower_lim, self.upper_lim + 1):
			parent_id = self.get_parent(leaf_id)
			while ( parent_id != -1 ):    # get_parent of 0 always returns -1
				if self.nodes[leaf_id].region_num not in self.nodes[parent_id].contained_regions:
					logging.debug('test FAILED')
					raise KeyError(str(parent_id) + ' does not contain region of leaf ' + str(leaf_id)  + '- inspect assemble_regions in IP class')
				parent_id = self.get_parent(parent_id)
		logging.debug('test PASSED')

	def get_computation_power(self, node_id):
		return self.computation_power[self.get_level(node_id)]
			
	def loop_step(self):
	
		#pool = Pool(processes = 8)
		#pool.map(self.step_through, range(0,self.upper_lim+1))
		#pool.terminate()
		for n in reversed(range(0, self.upper_lim + 1)):
			self.ip_process_without_gui(n) 

	

	def send_packet(self, _id,  _type, content_name, from_id, dest_id, ticks, *args):
		# Needed to seperate events that are scheduled to happen from getting mixed up in the current events
		# Step 1: Send_packets -> Step 2: Deliver_packets, makes them availible for processing
		if args:
			pack = Packet(_id, _type, str(content_name), from_id,  dest_id, args[0])
		else:
			pack = Packet(_id, _type, str(content_name), from_id,  dest_id)
		pack.ticks += (1 + ticks) # Latency in delivering a packet
		self.packets_to_be_delivered.append(pack)

	def deliver_packets(self):
		# Step 2 of 2, ofthe packet sending process
		while(self.packets_to_be_delivered): 
			pack = self.packets_to_be_delivered.pop()
			dest_id = pack.dest_id
			self.nodes[dest_id].incoming.append(pack)

	

	def packet_generator(self,size):
		logging.debug('packet_generator called, starting...')
		for i in range(0,size):
			content_name = self.content_names[random.randint(0,len(self.content_names)-1)]
			requester_id = self.get_random_leaf_machine()
			self.send_packet(0, 'request',content_name, requester_id ,requester_id,0)

	def standard_traffic(self):
		logging.debug('standard_traffic called, beggining packet_generator')
		self.packet_generator(self.packet_frequency) # This can be changed to suiting 
	
	def run_simulator(self, warm_up_seconds, loop_seconds, packet_gen_interval, logging_interval):
		self.sched.add_interval_job(self.standard_traffic,seconds=packet_gen_interval)
		self.sched.start()
		self.warm_up(warm_up_seconds)
		self.event_loop(loop_seconds, logging_interval)

	def warm_up(self,warm_up_seconds):
		logging.debug('phase 1 packet_generator complete, beggining sched and warm_up')
		start = time.time()
		end = time.time()
		while end-start <= warm_up_seconds:
			self.deliver_packets()
			self.loop_step()
			end=time.time()
			#self.packet_generator(50)

	def event_loop(self, seconds, logging_interval):
		self.sched.add_interval_job(self.log_level_congestion, seconds=logging_interval)
		self.sched.add_interval_job(self.log_rt_tick_times, seconds=logging_interval)
		self.sched.add_interval_job(self.log_packets_delivered, seconds=logging_interval)
		#self.sched.add_interval_job(self.log_rt_by_level, seconds=logging_interval)
		duration_seconds = seconds
		start = time.time()
		end = time.time()
		print 'start'
		while end-start <= duration_seconds:
			self.deliver_packets()
			self.loop_step()
			end = time.time()
		self.sched.shutdown()
		#self.write_level_congestions()
		self.write_rtt_means()
		#self.write_packets_delivered()
		#self.write_rt_by_level()

	def log_level_congestion(self):
		self.total_congestions.append(copy.deepcopy(self.level_congestion))

	def write_level_congestions(self):
		level_file = open("ip_level_congestion.csv","a")
		for dic in self.total_congestions:
			string = ''
			for key, value in dic.iteritems():
				string += str(value) + ','
			level_file.write(string.strip(',') + "\n")

	def log_rt_tick_times(self):
		self.ip_rt_tick_means.append(int(sum(self.ip_rt_tick_times)/len(self.ip_rt_tick_times)))
		self.ip_rt_tick_times = []

	def write_rtt_means(self):
		file_name = "ip_rtt" +  "-l=" + str(self.levels) + "-p="+ str(self.p) + "-q=" + str(self.q) +  ".csv"
		ip_rtt_file = open(file_name,"a")
		for mean in self.ip_rt_tick_means:
			ip_rtt_file.write(str(mean) + "\n")

	def log_packets_delivered(self):
		self.packets_delivered_slices.append(self.packets_delivered_count)
		self.packets_delivered_count = 0

	def write_packets_delivered(self):
		packets_file = open("ip_packets_delivered_slices.csv","a")
		for packets_count in self.packets_delivered_slices:
			packets_file.write(str(packets_count) + "\n")



	def region_contained(self, high_node_id, low_node_id):
		high_node = self.nodes[high_node_id]
		low_node = self.nodes[low_node_id]
		if low_node.region_num == 0:
			raise KeyError('low node region id was not properly declared')
		elif low_node.region_num in high_node.contained_regions:
			return True
		else:
			return False 

	def ip_process_without_gui(self, node_id):
		global process_start_time, process_end_time
		# higher level nodes have a faster computation model
		comp_power = self.computation_power[self.level_ranges_dict[node_id]]
		i = 0 
		while i < comp_power:

			if (self.nodes[node_id].incoming):
				logging.debug(' processing incoming packet at %d' % node_id)
				packet = self.nodes[node_id].incoming.popleft()
				logging.debug(" packet data: %s", str(packet)) 
				

				if packet.type == 'request':   
					  
					# Case 1: content in cache
					if packet.content_name in self.nodes[node_id].content_store:

						if packet.origin_id == node_id: # I am the source
						# Case where active request hasnt been created yet but content in cache
							logging.debug(" DONE! Content already cached, I am the source: %d" % node_id)
							self.ip_rt_tick_times.append(packet.ticks)
							self.packets_delivered_count += 1
						else:
							# If region is contained below this node - then forward it down, else send up to parent
							if self.region_contained(node_id, packet.origin_id):
								dest_id = self.nodes[node_id].forwarding(packet.origin_id)
							else:
								dest_id = self.get_parent(node_id)
							self.send_packet(packet.id, 'response', packet.content_name,  packet.origin_id, dest_id, packet.ticks, self.nodes[node_id].content_store[packet.content_name])
							logging.debug(" content %s already in cache", packet.content_name) 
							logging.debug(" sent content back along reverse path to node  %d ", dest_id)
							

					# Case 2: location of content lives in children, forward request to child, keep original origin_id of packet
					elif packet.content_name in self.nodes[node_id].forwarding_table:
						directed_child_id  = self.nodes[node_id].forwarding_table[packet.content_name]   #direction of child where destination node is contained 
						self.send_packet( packet.id, 'request', packet.content_name ,packet.origin_id, directed_child_id, packet.ticks)
						logging.debug(" forwarded request to child %d ", directed_child_id )
						

					# Case 3: location of content not known, send to parent, keep same origin id of packet
					else:
						parent_id = self.get_parent(node_id)
						self.send_packet(packet.id, 'request', packet.content_name, packet.origin_id , parent_id, packet.ticks )
						logging.debug(" content %s NOT known sent request to parent %d", packet.content_name, parent_id) 
						self.nodes[node_id].local_tick_count[packet.id] = packet.ticks
					 

				elif packet.type == 'response':
					# packet is a response

					# Case 1: node is source of request
					if packet.origin_id == node_id:
						self.ip_rt_tick_times.append(packet.ticks)
						self.packets_delivered_count += 1
						logging.debug(" DONE! I am the source: %d" % node_id)
												
					# Case 2: node was a middle man
					else:
						print logging.debug("Forwarding response along to requesters, I am: %d ... ", node_id)
						
						# If region is contained below this node - then forward it down, else send up to parent
						if self.region_contained(node_id, packet.origin_id):
							dest_id = self.nodes[node_id].forwarding(packet.origin_id)
						else:
							dest_id = self.get_parent(node_id)

						self.send_packet(packet.id, 'response', packet.content_name, packet.origin_id, dest_id, packet.ticks, packet.content_data) 			
						logging.debug("Sent response back along reverse path to %d ", dest_id)
					
					# Now that all packets have been process cache the content data 
					self.nodes[node_id].cache_content(packet.content_name, packet.content_data)
					logging.debug(" Added content (%s) to content store"  % packet.content_name)
				
				else:
					logging.warning(' Mislabeled Packet')

			i += 1
		for packet in self.nodes[node_id].incoming:
			packet.ticks += 1







	## Utility Functions for Network Accessability 
	def get_level(self, node_id):
		return self.level_ranges_dict[node_id]

		logging.debug('Incorrect Node ID given at get_level')

	def set_up_cache(self):
		for node_id in self.nodes:
			level = self.get_level(node_id)
			self.nodes[node_id].cache_max = self.cache_slots[level]

	def loop(self):
		self.deliver_packets()
		self.loop_step()

	def get_other_leaf_machine(self,node_id):
		x = node_id
		while x == node_id:
			x = random.randint(self.lower_lim, self.upper_lim)
		return x

	def get_random_leaf_machine(self):
		leaf_id = 7 
		while leaf_id % 7 == 0: 
			leaf_id = random.randint(self.lower_lim+1, self.upper_lim)
		return leaf_id
	
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
		if n == 0: 
			return -1
		if (n <= 7):
			return 0 
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
		if len(self.nodes[node_id].incoming) > 0:
			packet = self.nodes[node_id].incoming[0]
			if packet['_type'] == 'response':
				return {'color':'purple', 'width':2.0}

		if node_id == 2200 and len(self.nodes[node_id].incoming) == 0:
			return {'color':'green', 'width':2.0}

		if node_id <= 8:
			if size <= 0:
				return {'color':'grey', 'width':1.0}
			elif size < 20:
				return {'color':'blue', 'width':2.0}
			elif size < 30:
				return {'color':'deep sky blue', 'width':2.0}
			elif size < 40:
				return {'color':'cyan', 'width':2.0}
			elif size < 50:
				return {'color':'green', 'width':2.0}
			elif size < 60:
				return {'color':'yellow', 'width':2.0}
			elif size < 70:
				return {'color':'orange', 'width':2.0}
			elif size < 80:
				return {'color':'dark orange', 'width':2.0}
			elif size < 90:
				return {'color':'orange red', 'width':2.0}
			else: 
				return {'color':'red', 'width':2.0}

		else:
			if size <= 0:
				return {'color':'grey', 'width':1.0}
			elif size < 5:
				return {'color':'blue', 'width':2.0}
			elif size < 10:
				return {'color':'deep sky blue', 'width':2.0}
			elif size < 15:
				return {'color':'cyan', 'width':2.0}
			elif size < 20:
				return {'color':'green', 'width':2.0}
			elif size < 25:
				return {'color':'yellow', 'width':2.0}
			elif size < 30:
				return {'color':'orange', 'width':2.0}
			elif size < 35:
				return {'color':'dark orange', 'width':2.0}
			elif size < 40:
				return {'color':'orange red', 'width':2.0}
			else: 
				return {'color':'red', 'width':2.0}
		

	
		

##
# End of Program
##