
from unittest import *
from Simulator import * 


ip=IP_Network(4,False)
ip.prepare()
ip.assemble_regions()	
ip.test_regionality_topdown()

def sent():
	for pack in ip.packets_to_be_delivered:
		print pack.ticks


nb=NB_Network(4,False)
nb.prepare()

def test_packets_to_be_delivered():
	nb.send_packet('request',10001,-1,500,0)
	nb.send_packet('request',10001,-1,500,0)


def test_pending_requests():
	nb.send_packet('request',10001,-1,500,0)
	nb.send_packet('request',10001,-1,500,0)



	((-1 in nb.nodes[500].pending_table['10001']) and (len(nb.nodes[500].pending_table['10001'])==1))