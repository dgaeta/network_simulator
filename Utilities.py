# Utility functions for Network Simulation
# 
# author: Daniel Gaeta 
import Tkinter as tk
from time import sleep
import math
import logging
import Servers 
import random
import sys



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