##
# Used for debugging and testing
##








from Simulator import *
nb=NB_Network(4,False)
nb.prepare()
nb.run_simulator(60,60,1,2)

from Simulator import * 
ip=IP_Network(4,False)
ip.prepare()
ip.assemble_regions()
ip.run_simulator(60,60,1,2)

self = ip
content_name = self.content_names[random.randint(0,len(self.content_names)-1)]
requester_id = self.get_random_leaf_machine()
self.send_packet('request',content_name, requester_id ,requester_id,0)
self.deliver_packets()




from Simulator import *
ip=IP_Network(4,False)
ip.assemble_regions()
ip.test_regionality_topdown()


nb.run_simulator(60,60,1,2)