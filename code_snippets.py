##
# Used for debugging and testing
##

from Simulator import *
network=Network(4,False)
network.prepare()
network.run_simulator(20,20)


network.send_packet('request','10466',0,1345, 0)


network.deliver_packets()
network.loop_step()




with open('level_congestion.csv', 'wb') as csvfile:
			self.lc = csv.writer(csvfile, delimiter=' ')
			self.lc.writerow(str(self.level_congestion) + "\n")




lap=0
def timer():
    start=time.time()
    print 'start'
    while end-start <= 10:
        print 'ok'
        end = time.time()



test_file = open("test.csv","a")
	for i in range(0,4
			test_file.write(str(i) + "\n")




from Simulator import *
network=Network(3,True)
