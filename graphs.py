nb_means = []
nb_rtt_means4 = []
with open('nb_rtt4.csv', 'rb') as rtt:
    reader = csv.reader(rtt)
    for row in reader:
        nb_rtt_means4.append(int(row[0]))
nb_means.append(int(sum(nb_rtt_means4)/len(nb_rtt_means4)))

nb_rtt_means5 = []
with open('nb_rtt5.csv', 'rb') as rtt:
    reader = csv.reader(rtt)
    for row in reader:
        nb_rtt_means5.append(int(row[0]))      
nb_means.append(int(sum(nb_rtt_means5)/len(nb_rtt_means5))) 


nb_rtt_means6 = []
with open('nb_rtt6.csv', 'rb') as rtt:
    reader = csv.reader(rtt)
    for row in reader:
        nb_rtt_means6.append(int(row[0]))
nb_means.append(int(sum(nb_rtt_means5)/len(nb_rtt_means5)))







ip_means = []        
ip_rtt_means4 = []
with open('ip_rtt4.csv', 'rb') as rtt:
    reader = csv.reader(rtt)
    for row in reader:
        ip_rtt_means4.append(int(row[0]))
ip_means.append(int(sum(ip_rtt_means4)/len(ip_rtt_means4)))        

ip_rtt_means5 = []
with open('ip_rtt5.csv', 'rb') as rtt:
    reader = csv.reader(rtt)
    for row in reader:
        ip_rtt_means5.append(int(row[0]))
ip_means.append(int(sum(ip_rtt_means5)/len(ip_rtt_means5)))        

ip_rtt_means5 = []
with open('ip_rtt6.csv', 'rb') as rtt:
    reader = csv.reader(rtt)
    for row in reader:
        ip_rtt_means6.append(int(row[0]))
ip_means.append(int(sum(ip_rtt_means6)/len(ip_rtt_means6)))     




N = 3
ind = np.arange(N)
width = 0.35

fig, ax = plt.subplots()
rects1 = ax.bar(ind, nb_means, width, color='r')
rects2 = ax.bar(ind+width, ip_means, width, color='y')

# add some
ax.set_ylabel('Ticks')
ax.set_xlabel('Network Depth')
ax.set_title('Total Time to Fulfill Requests Over all Levels by Depth')
ax.set_xticks(ind+width)
ax.set_xticklabels( ('4', '5', '6') )

ax.legend( (rects1[0], rects2[0]), ('NB', 'IP') )

plt.show()


