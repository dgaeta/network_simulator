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


from NB_Network import * 
from IP_Network import * 


def run_nb(levels, warm_up_seconds, loop_seconds, packet_gen_interval, packet_amount, logging_interval):
	nb=NB_Network(4,False)
	nb.packet_frequency = packet_amount
	nb.prepare()
	nb.run_simulator(warm_up_seconds, loop_seconds, packet_gen_interval, logging_interval)
	print nb.packets_delivered_count


def run_ip(levels, warm_up_seconds, loop_seconds, packet_gen_interval, packet_amount, logging_interval):
	ip=IP_Network(4,False)
	ip.prepare()
	ip.packet_frequency = packet_amount
	ip.assemble_regions()	
	ip.test_regionality_topdown()
	ip.run_simulator(warm_up_seconds,loop_seconds, packet_gen_interval, logging_interval)
	print ip.packets_delivered_count
	
def nb_gui(levels):
	nb=NB_Network(levels,True)
		

def ip_gui(levels):
	ip=IP_Network(levels,True)		

##
# End of Program
##