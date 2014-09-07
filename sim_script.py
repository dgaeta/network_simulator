from subprocess import call


def make_command_array(system_type,levels,p,q):
	commands_arr = []
	commands_arr.append('python')
	commands_arr.append('from Simulator import *')
	commands_arr.append(str('nb=NB_Network(' + str(4)+',False,'+ str(p) +',' + str(q) + ')'))
	commands_arr.append('nb.run_simulator(1200,1200,2,10))')
	return commands_arr

def execute_commands(system_type,levels,p_arr, q_arr):
	p = float(p_arr.pop())/10
	q = float(q_arr.pop())/10
	print 'Running Simulator for ' + str(system_type) + ' levels= ' + str(levels) + ' p=' + str(p) + ' q=' + str(q)
	commands_arr = make_command_array(system_type,levels,p,q)
	call(commands_arr)


p_max = .8
q_max = .8

ps = [x for x in range(2,int(p_max*10)+1) if x%2==0]
qs = [y for y in range(2,int(q_max*10)+1) if y%2==0]

system_type = 'nb'
levels = 4

execute_commands(system_type,levels,ps,qs)