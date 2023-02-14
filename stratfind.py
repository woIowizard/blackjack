import argparse,datetime
import numpy as np

edges = np.array([-0.01302434801760524,-0.011908562279274669,-0.01080130089010126,-0.009782218561846107,-0.00894901433748832,-0.008396243206847816,-0.007258715015973558,-0.006775214055637279,-0.005628302794730593,-0.004765129528246249,-0.0038635863120416356,-0.00330061537657059,-0.001995837861451646,-0.0013194588595324594,-0.002513224716748848,0.0005293426651101526,0.0013550902515568198,0.0021298033756847663,0.003209325400909519, 0.0042026840768633065, 0.004810944675226022, 0.005500114718764763, 0.006733485250155465, 0.007515990183737213, 0.008526629353955165, 0.00931754065882899])
three_pockets = np.array([1.388e-05, 7.984e-05, 0.000794, 0.00404058, 0.01309942, 0.03110434, 0.05686078, 0.08891252, 0.11648958, 0.13554564, 0.13813754, 0.12522472, 0.10216868, 0.07526086, 0.05014146, 0.03035748, 0.01674986, 0.00842468, 0.00389502, 0.00166914, 0.00066124, 0.00024186, 8.546e-05, 2.914e-05, 8.54e-06, 3.74e-06])
four_pockets = np.array([0.0001777, 0.0008598, 0.0032596, 0.00923714, 0.02057002, 0.03844204, 0.06158872, 0.08681002, 0.10847384, 0.12223872, 0.12454376, 0.11529116, 0.09750388, 0.07566108, 0.05405622, 0.0355505, 0.02160006, 0.01218246, 0.00641168, 0.00312868, 0.00142076, 0.00060672, 0.00024112, 9.418e-05, 3.282e-05, 1.732e-05])
five_pockets = np.array([0.0009696, 0.00246388, 0.00640488, 0.01392662, 0.02613614, 0.04312336, 0.06348248, 0.08431588, 0.10182704, 0.11265416, 0.11451148, 0.10741242, 0.09316238, 0.07493928, 0.05619134, 0.03920704, 0.02553556, 0.0155708, 0.0089034, 0.00479584, 0.0024185, 0.0011658, 0.00051724, 0.00021802, 9.042e-05, 5.644e-05])

minimum,start,end,min_acceptable = 25,0,None,0

p = argparse.ArgumentParser()
p.add_argument('-m',help='minimum bet (default %s)'%minimum)
p.add_argument('-s',help='starting value of x (default %s)'%start)
p.add_argument('-e',help='ending value of x (default %s)'%end)
p.add_argument('-b',help='minimum acceptable edge (default %s)'%min_acceptable)
args = p.parse_args()

try: assert len(edges) == 26
except: 
    print('edges vector in incorrect format (current length %s, expected 26)'%len(edges))
    quit()
try: assert len(three_pockets) == 26
except: 
    print('3 pockets transition vector in incorrect format (current length %s, expected 26)'%len(three_pockets))
    quit()
try: assert len(four_pockets) == 26
except: 
    print('4 pockets transition vector in incorrect format (current length %s, expected 26)'%len(four_pockets))
    quit()
try: assert len(five_pockets) == 26
except: 
    print('5 pockets transition vector in incorrect format (current length %s, expected 26)'%len(five_pockets))
    quit()

try:
    assert int(args.m) >= 0
    minimum = int(args.m)
except: 
    if args.m: print('[%s] -m option invalid. minimum bet defaulting to %s'%(datetime.datetime.now().replace(microsecond=0),minimum))
try:
    assert int(args.s) >= 0
    start = int(args.s)
except: 
    if args.s: print('[%s] -s option invalid. starting value defaulting to %s'%(datetime.datetime.now().replace(microsecond=0),start))
try:
    assert int(args.e) >= start
    end = int(args.e)
except: 
    if args.e: print('[%s] -e option invalid. ending value defaulting to %s'%(datetime.datetime.now().replace(microsecond=0),end))
try:
    assert float(args.b) >= 0
    min_acceptable = float(args.b)
except: 
    if args.b: print('[%s] -b option invalid. min acceptable edge defaulting to %s'%(datetime.datetime.now().replace(microsecond=0),min_acceptable))

print('[%s] looking for strategy with edge >=%s from x=%s%s. min bet: $%s'%(datetime.datetime.now().replace(microsecond=0),min_acceptable,start,' to %s'%end if end else '',minimum))

num_neg = len([c for c in edges if c < 0])

def get_freq(pocket_strat):
    transition_matrix = []
    ref = [three_pockets,four_pockets,five_pockets]
    for pocket_number in pocket_strat: transition_matrix.append(ref[pocket_number-3])
    transition_matrix = np.array(transition_matrix).transpose()
    transition_matrix -= np.eye(len(pocket_strat))
    transition_matrix[-1] = [1]*len(pocket_strat)
    transition_matrix = np.linalg.inv(transition_matrix)
    return(transition_matrix.transpose()[-1])
    
def get_EV(num3,num4,x,minimum,edges): 
    pocket_strat = [3]*num3 + [4]*num4 + [5]*(26-num3-num4)
    freqs = get_freq(pocket_strat)
    ave_EV,ave_spend = 0,0
    for i in range(26):
        if i < num_neg:
            ave_EV += freqs[i]*edges[i]*pocket_strat[i]*minimum
            ave_spend += freqs[i]*pocket_strat[i]*minimum
        else:
            ave_EV += freqs[i]*edges[i]*pocket_strat[i]*25*x*(i-10)
            ave_spend += freqs[i]*pocket_strat[i]*25*x*(i-10)
    return ave_EV, ave_spend

best_EV,best_spend = -99,1
x = max(minimum//25-1,start-1)

while best_EV/best_spend < min_acceptable:
    x += 1
    if end and x > end: 
        print('[%s] failed to find any strategy with edge at least %s'%(datetime.datetime.now().replace(microsecond=0),min_acceptable))
        quit()
    print('[%s] Trying x = %s'%(datetime.datetime.now().replace(microsecond=0),x))
    best_num3,best_num4 = -99,-99
    for num3 in range(num_neg+1):
        for num4 in range(num_neg+1-num3):
            this_EV,this_spend = get_EV(num3,num4,x,minimum,edges)
            if this_EV > best_EV: best_EV,best_num3,best_num4,best_spend = this_EV,num3,num4,this_spend
else:
    print('[%s] optimum strategy found with EV $%s/round and player edge %s%%'%(datetime.datetime.now().replace(microsecond=0),round(best_EV,4),round(best_EV/best_spend*100,4)))
    pocket_strat = [3]*best_num3 + [4]*best_num4 + [5]*(26-best_num3-best_num4)
    betting_strat = [minimum]*num_neg + [i*x*25 for i in range(-10+num_neg,16)]
    freqs = get_freq(pocket_strat)
    per_round_ev = [pocket_strat[i]*betting_strat[i]*freqs[i]*edges[i] for i in range(26)]
    print('\nCOUNT\tFREQUENCY\t\t\tPOCKETS\t\tBET\t\tEV')
    print('='*90)
    for i in range(26): print('{0}\t{1:<20}\t\t{2}\t\t{3}\t\t{4}'.format(i-10,freqs[i],pocket_strat[i],betting_strat[i],per_round_ev[i]))
   