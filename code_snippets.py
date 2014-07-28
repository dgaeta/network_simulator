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


	congestion = 0 
	node_level = 0
	for n in range(0, 8):
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








-----------

nb_rtt_means4 = []
with open('nb_rtt4.csv', 'rb') as rtt:
    reader = csv.reader(rtt)
    for row in reader:
        nb_rtt_means4.append(int(row[0]))
        
        
ip_rtt_means4 = []
with open('ip_rtt4.csv', 'rb') as rtt:
    reader = csv.reader(rtt)
    for row in reader:
        ip_rtt_means4.append(int(row[0]))
        
nb_mean4 = int(sum(nb_rtt_means4)/len(nb_rtt_means4))
ip_mean4 = int(sum(ip_rtt_means4)/len(ip_rtt_means4))
arr = [nb_mean4, ip_mean4]

rtt_pd4 = pd.DataFrame(np.array(arr))
        
#print len(wValues), len(wDownByte)

plt.figure(figsize=(7, 8))
width = 0.2
ind = [0, 0.2]
plt.bar([0.5], (nb_mean4), width, color = 'b', label = 'Name-Based')
plt.bar([1], (ip_mean4), width, color = 'g', label = 'Standard-IP')
plt.ylabel('Ticks')
plt.xlabel('Routing System')
plt.title('Average Number of Ticks to Recieve Response Over All Levels')
plt.xticks([0.625, 1.125], ('Name-Based', 'Standard-IP') )
plt.legend( (rects1[0], rects2[0]), ('Name Based', 'IP',) )
plt.show()



