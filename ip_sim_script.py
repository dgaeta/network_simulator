from Simulator import *

def execute_command(system_type,levels,pq_pair, req_freq):
	p = float(pq_pair[0])/10
	q = float(pq_pair[1])/10
	print 'Running Simulator for ' + str(system_type) + ' levels= ' + str(levels) + ' p=' + str(p) + ' q=' + str(q)
	ip=IP_Network(levels,False, p, q)
	ip.run_simulator(1800,1800,req_freq,10)


p_max = .8 * 10
q_max = .8 * 10 

pairs = []
for p in [x for x in range(2,int(p_max)+1) if x%2==0]:
        for q in [y for y in range(2,int(q_max)+1) if y%2==0]:
        	pairs.append([p,q])

system_type = 'ip'
levels = 4
requests_frequency = 5 #seconds

def run(lev):
	levels = lev
	while len(pairs) > 0:
		pq = pairs.pop()
		execute_command(system_type,levels,pq,requests_frequency)