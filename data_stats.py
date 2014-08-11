import csv
import numpy as np
#import matplotlib.pyplot as plt
#import pylab as py
#import pandas as pd



def p2q2_std(network_type):
	data= []
	file_name = str(network_type) + '_rtt-l=4-p=0.2-q=0.2.csv'
	with open(file_name, 'rb') as rtt:
		reader= csv.reader(rtt)
		for row in reader:
			data.append(int(row[0]))
	mean= sum(data)/len(data)
	std = np.std(np.array(data))
	return std

