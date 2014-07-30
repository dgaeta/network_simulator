import csv
import numpy as np
import matplotlib.pyplot as plt
import pylab as py
import pandas as pd




def rtt_means():
    
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
    try:
        with open('nb_rtt6.csv', 'rb') as rtt:
            reader = csv.reader(rtt)
            for row in reader:
                nb_rtt_means6.append(int(row[0]))
        nb_means.append(int(sum(nb_rtt_means6)/len(nb_rtt_means6)))
    except IOError:
        nb_means = 0





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



    ip_rtt_means6 = []
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
    ax.set_xticklabels( ('lowest 4', '5', '6 highest') )

    ax.legend( (rects1[0], rects2[0]), ('NB', 'IP') )

    plt.show()



def average_difference():
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
    nb_means.append(int(sum(nb_rtt_means6)/len(nb_rtt_means6)))

    ###

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

    ip_rtt_means6 = []
    with open('ip_rtt6.csv', 'rb') as rtt:
        reader = csv.reader(rtt)
        for row in reader:
            ip_rtt_means6.append(int(row[0]))
    ip_means.append(int(sum(ip_rtt_means6)/len(ip_rtt_means6)))     

    avg_diff = []
    level = 4
    for i in range(0,3):
        avg_diff.append((ip_means[i] - nb_means[i])/level)
        level+=1 


    fig, ax = plt.subplots()

    ax.plot(np.array(avg_diff), '-o', ms=20, lw=2, alpha=0.7, mfc='orange')
    ax.set_xticklabels( ('lowest 4', '', '5', '',  '6 highest') )
    ax.grid()

    plt.show()
