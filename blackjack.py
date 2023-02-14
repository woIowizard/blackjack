import argparse,datetime,random

buffer,decks,pockets,bet,report = 7,6,5,25,1000000

p = argparse.ArgumentParser()
p.add_argument('-n',help='number of rounds')
p.add_argument('-B',help='CSM buffer (default %s)'%buffer)
p.add_argument('-D',help='CSM deck size (default %s)'%decks)
p.add_argument('-c',help='force count. single value, \'[min],[max]\', or \'A\' for -10 to +15. \'m\' for negative values')
p.add_argument('-b',help='bet amount for uniform betting strategy (default %s)'%bet)
p.add_argument('-p',help='number of pockets for uniform betting strategy (default %s)'%pockets)
p.add_argument('-S',help='non-uniform betting strategy (4 integer params)')
p.add_argument('-r',help='report points (default %s)'%report)
p.add_argument('-d',action='store_true',help='implement deviations from basic strategy')
p.add_argument('-V',action='store_true',help='run one round with verbosity')
p.add_argument('-T',action='store_true',help='report only transition probabilities')
p.add_argument('-o',help='outfile')
args = p.parse_args()

# input validation
try: 
    if args.n[-1] == 'M': n = 1000000*int(args.n[:-1])
    else: n = int(args.n)
    assert n > 0
except: n = 1
try: 
    if args.c == 'A': c = range(-10,16)
    elif ',' not in args.c: c = [int(args.c)]
    else: c = range(int(args.c.replace('m','-').split(',')[0]),int(args.c.replace('m','-').split(',')[1])+1)
except: c = [None]
try:
    assert int(args.B) >= 0
    buffer = int(args.B)
except: 
    if args.B: print('[%s] -B option invalid. CSM buffer defaulting to %s'%(datetime.datetime.now().replace(microsecond=0),buffer))
try:
    assert int(args.D) >= 0
    decks = int(args.D)
except: 
    if args.D: print('[%s] -D option invalid. CSM decks defaulting to %s'%(datetime.datetime.now().replace(microsecond=0),decks))
try:
    assert int(args.b) >= 0
    bet = int(args.b)
except: 
    if args.b: print('[%s] -b option invalid. minimum bet defaulting to %s'%(datetime.datetime.now().replace(microsecond=0),bet))
try:
    assert int(args.p) >= 0
    pockets = int(args.p)
except: 
    if args.p: print('[%s] -p option invalid. number of pockets defaulting to %s'%(datetime.datetime.now().replace(microsecond=0),pockets))
try:
    if args.r[-1] == 'M': temp = 1000000*int(args.r[:-1])
    else: temp = int(args.r)
    assert temp > 0
    report = temp
except: 
    if args.r: print('[%s] -r option invalid. report point defaulting to %s'%(datetime.datetime.now().replace(microsecond=0),report))
    
if args.V: 
    n,c = 1,[None]
print('[%s] running %s round %ssimulation with %s'%(datetime.datetime.now().replace(microsecond=0),n,'verbose ' if args.V else '','deviations' if args.d else 'basic strategy'))

# parse strategy
strat = (pockets,bet)
if args.S:
    try: 
        temp = [int(c) for c in args.S.split(',')]
        assert len(temp) == 4 and temp[3] > 0 and temp[1] > 0
        strat = temp
    except: print('[%s] -S option invalid, defaulting to uniform'%(datetime.datetime.now().replace(microsecond=0)))

if len(strat) == 2: print('[%s] strategy: uniform. pockets: %s, bet: %s'%(datetime.datetime.now().replace(microsecond=0),pockets,bet))
else: print('[%s] strategy: counting. pockets: 3 up to count %s, 5 after. bets: %s up to count %s, %s*count after'%(datetime.datetime.now().replace(microsecond=0),strat[0],strat[1],strat[2],strat[3]*strat[1]))

# continuous shuffling machine
class CSM():
    def __init__(self,n,buffer):
        self.n = n
        self.buffer = buffer
        self.deck = ['A',2,3,4,5,6,7,8,9,10,'J','Q','K']*4*n
        random.shuffle(self.deck)

    def deal(self): return self.deck.pop()
    
    def set_count(self,count):
        bigs = ['A',10,'J','Q','K']*4*self.n
        smalls = [2,3,4,5,6]*4*self.n
        mids = [7,8,9]*4*self.n
        
        if count > 0:
            random.shuffle(smalls)
            for _ in range(count): smalls.pop()
        elif count < 0:
            random.shuffle(bigs)
            for _ in range(-count): bigs.pop()
        
        self.deck = bigs + smalls + mids
        random.shuffle(self.deck)
   
    def restore(self,hand):
        to_shuffle = self.deck[:-self.buffer] + hand
        to_keep = self.deck[-self.buffer:]
        random.shuffle(to_shuffle)
        self.deck = to_shuffle + to_keep

# players' hands
class Hand():
    def __init__(self,n,card):
        self.n = n
        self.hand = [card]
        self.alive = True
        self.double = False
        self.split = False
        self.surrender = False
        self.blackjack = False
        self.bust = False
        self.hard = False
        
    def draw(self,card):
        self.hand.append(card)
        self.value = value(self.hand)
        if self.value > 21: self.bust = True
        else:
            hard_value = 0
            for i in self.hand: hard_value += i if i not in ['A','J','Q','K'] else (1 if i == 'A' else 10)
            self.hard = self.value == hard_value
    
    def check_blackjack(self): 
        self.blackjack = self.value == 21
        if self.blackjack: self.alive = False
    
# function to compute the value of a hand
def value(hand): 
    total = 0
    for j in hand: total += j if j not in ['A','J','Q','K'] else (11 if j == 'A' else 10)
    for i in range(hand.count('A')):
        if total <= 21: break
        else: total -= 10
    return total

# function to get the count of a round
def get_count(hand):
    count = 0
    for card in hand:
        if card in [2,3,4,5,6]: count += 1
        elif card in ['A',10,'J','Q','K']: count -= 1
    return count

# function to check whether a hand should split
def should_split(hand,exposed,count,deviate):
    card = hand.hand[0]
    # if not a pair, cannot split
    if value([card]) != value([hand.hand[1]]): return False
    
    # deviations
    if deviate: pass
        # deviation: if count >= 8, also split As against A
        #if deviate and count >= 8 and card == 'A' and exposed == 11: return True
        # deviation: if count <= -8, also split 9s against 7
        #if deviate and count <= -8 and card == 9 and exposed == 7: return True
        # deviation: if count >= 8, don't split 8s against 9
        #if deviate and count >= 8 and card == 8 and exposed == 9: return True
        
    # split As against anything other than A
    if card == 'A' and exposed != 11: return True
    # split 9s against 2-6 or 8-9
    if card == 9 and (exposed in range(2,7) or exposed in range(8,10)): return True
    # split 8s against 2-9
    if card == 8 and exposed in range(2,10): return True
    # split 7s against 2-7
    if card == 7 and exposed in range(2,8): return True
    # split 6s against 2-6
    if card == 6 and exposed in range(2,7): return True
    # split 4s against 5 or 6
    if card == 4 and exposed in range(5,7): return True
    # split 2s or 3s against 2-7
    if card in range(2,4) and exposed in range(2,8): return True
    # anything else, don't split
    return False

# function to check whether a hand should surrender
def should_surrender(hand,exposed,count,deviate):
    # split hands cannot surrender
    if hand.split: return False
    # soft hands don't surrender
    if not hand.hard: return False
    
    # deviations
    if deviate: pass
        # deviation: if count <= -8, hard 14 don't surrender
        #if deviate and count <= -8 and hand.value == 14: return False
    
    # hard 14-16 surrender against 10
    if hand.value in range(14,17) and exposed == 10: return True
    # hard 16 also surrenders against 9
    if hand.value == 16 and exposed == 9: return True
    # anything else, don't surrender
    return False

# function to check whether a hand should double
def should_double(hand,exposed,count,deviate): 
    # split As cannot double
    if hand.split and hand.hand[0] == 'A': return False
    
    # deviations
    if deviate: pass
        # deviation: if count <= -8 double on soft 17-18 against 2
        #if not hand.hard and count <= -8 and hand.value in range(17,19) and exposed == 2: return True
    
    # hard hands
    if hand.hard:
        # hard 9 doubles against 3-6
        if hand.value == 9 and exposed in range(3,7): return True
        # hard 10-11 double against 2-9
        if hand.value in range(10,12) and exposed in range(2,10): return True
    # soft hands
    else:
        # soft 13-14 double against 5-6
        if hand.value in range(13,15) and exposed in range(5,7): return True
        # soft 15-16 double against 4-6
        if hand.value in range(15,17) and exposed in range(4,7): return True
        # soft 17-18 double against 3-6
        if hand.value in range(17,19) and exposed in range(3,7): return True
    return False

# function to check whether a hand should hit
def should_hit(hand,exposed,count,deviate): 
    # split A cannot hit
    if hand.split and hand.hand[0] == 'A': return False
    # bust hands cannot hit
    if hand.bust: return False
    # doubled hands cannot hit
    if hand.double: return False
    
    # deviations
    if deviate: pass
    
    # hard hands
    if hand.hard:
        # hard 5-11 hit
        if hand.value in range(5,12): return True
        # hard 12 hit against all but 4-6
        if hand.value == 12 and exposed not in range(4,7): return True
        # hard 13-16 hit against 7-A
        if hand.value in range(13,17) and exposed in range(7,12): return True
    # soft hands
    else:
        # soft 13-17 hit
        if hand.value in range(13,18): return True
        # soft 18 hit against 9-A
        if hand.value == 18 and exposed in range(9,12): return True
    return False
  
# main function, plays one round
def play_one_round(pockets,bet,deck,count=None,verbose=False,deviate=False):
    win,bets,profits = 0,0,0
    
    ### initial deal
    table = []
    # deal one card to each pocket
    for i in range(pockets): table.append(Hand(i+1,deck.deal()))
    # one card to dealer
    table.append(Hand(0,deck.deal()))
    exposed = value([table[-1].hand[0]])
    # one more card to each pocket
    for i in range(pockets): table[i].draw(deck.deal())
        
    if verbose:
        print('\n===== Initial deal =====')
        for i in range(pockets): print('Pocket %s has %s'%(table[i].n,table[i].hand))
        print('Dealer draws %s'%(table[-1].hand[0]))

    ### each pocket plays in turn
    if verbose: print('\n===== Play =====')
    i = 0
    while i < len(table)-1:
        hand = table[i]
        if verbose: print('Pocket %s to play with %s'%(hand.n,hand.hand))

        ## if hand didn't come from a split, can consider blackjack, split, and surrender
        if not hand.split: 
            
            # check for blackjack
            hand.check_blackjack()
            if hand.blackjack:
                if verbose: print('Pocket %s has blackjack\n'%(hand.n))
                i += 1
                continue
            
            ## consider whether to split
            if should_split(hand,exposed,count,deviate):
                card = hand.hand[0]
                
                # draw 2 cards for split hands
                drawn = [deck.deal(),deck.deal()]
                if verbose: print('Splitting %ss against %s, drew %s and %s'%(card,exposed,drawn[0],drawn[1]))
             
                # if not splitting A, can split up to 3 times
                splits = 1
                while splits < 3 and card != 'A':
                    if card not in drawn: break
                    drawn.pop(drawn.index(card))
                    drawn += [deck.deal(),deck.deal()]
                    if verbose: print('Splitting %ss again, drew %s and %s'%(card,drawn[-1],drawn[-2]))
                    splits += 1

                # one card goes to original split hand
                hand.hand.pop()
                hand.draw(drawn[-1])
                if verbose: print('Present pocket is now %s'%(hand.hand))
                hand.split = True

                # create pockets for split hands
                for newcard in drawn[:-1]:
                    if verbose: print('Creating pocket %s with %s'%(len(table),[card,newcard]))
                    table = table[:-1] + [Hand(len(table),card)] + [table[-1]]
                    table[-2].draw(newcard)
                    table[-2].split = True
            
            # consider whether to surrender
            if should_surrender(hand,exposed,count,deviate):
                if verbose: print('Pocket %s surrenders with %s against %s\n'%(hand.n,hand.hand,exposed))
                hand.surrender = True
                hand.alive = False
                i += 1
                continue
        
        # consider whether to double
        if should_double(hand,exposed,count,deviate):
            bets += bet
            hand.double = True
            drawn = deck.deal()
            if verbose:
                if hand.hard: print('Pocket %s doubles on hard %s against %s'%(hand.n,hand.value,exposed))
                else: print('Pocket %s doubles on soft %s against %s'%(hand.n,hand.value,exposed))
            hand.draw(drawn)
            if verbose: print('Drew %s and now has %s with %s'%(drawn,hand.value,hand.hand))
        
        # consider whether to hit
        while should_hit(hand,exposed,count,deviate): 
            drawn = deck.deal()
            if verbose: 
                if hand.hard: print('Hit with hard %s against %s, drew %s and now has %s'%(hand.value,exposed,drawn,hand.hand+[drawn]))
                else: print('Hit with soft %s against %s, drew %s and now has %s'%(hand.value,exposed,drawn,hand.hand+[drawn]))
            hand.draw(drawn)
        
        # check if bust; if not, stand
        if hand.bust: 
            if verbose: print('Pocket %s bust\n'%(hand.n))
            hand.alive = False
        elif verbose: 
            if hand.hard: print('Pocket %s stands with hard %s against %s\n'%(hand.n,hand.value,exposed))
            else: print('Pocket %s stands with soft %s against %s\n'%(hand.n,hand.value,exposed))
        
        i += 1
        
    bets += bet*(len(table)-1)
    
    ### if any hand is still alive, dealer plays
    if sum([hand.alive for hand in table[:-1]]):
        if verbose: print('Dealer to play')
        
        # dealer draws a card, then checks for blackjack
        table[-1].draw(deck.deal())
        if verbose: print('Dealer draws %s'%(table[-1].hand[-1]))
        table[-1].check_blackjack()
        
        # if dealer has blackjack, round ends
        if table[-1].blackjack:
            if verbose: print('Dealer has blackjack')

        # if dealer has no blackjack, play on
        else:
            if verbose: print('Dealer has no blackjack')    

            # hit till >= 17
            while table[-1].value < 17:
                table[-1].draw(deck.deal())
                if verbose: print('Dealer draws %s, hand value now at %s'%(table[-1].hand[-1],table[-1].value))

            if verbose:
                # if dealer exceeds 21, bust
                if table[-1].value > 21: print('Dealer bust at %s with %s'%(table[-1].value,table[-1].hand))
                # else, stand
                else: print('Dealer stands at %s with %s'%(table[-1].value,table[-1].hand))
    
    # collect stats
    if verbose: print('\n===== Payout =====')
    
    # if dealer blackjack, only consider initial hands
    if table[-1].blackjack: 
        for hand in table[:pockets]:
            
            # surrendered hands lose 0.5x
            if hand.surrender:
                profits -= 0.5*bet
                if verbose: print('Pocket %s surrenders for loss of %s'%(hand.n,0.5*bet))
                    
            # blackjack hands push
            elif hand.blackjack:
                if verbose: print('Pocket %s standoff for blackjack against dealer blackjack'%(hand.n))
                    
            # all others lose 
            else:
                profits -= bet
                if hand.double:
                    profits -= bet
                    if verbose: print('Pocket %s loses %s for double against dealer blackjack'%(hand.n,2*bet))
                elif verbose: print('Pocket %s loses %s for dealer blackjack'%(hand.n,bet))
    
    # if dealer no blackjack, consider all hands
    else:
        for hand in table[:-1]:
            
            # blackjacks win 1.5x
            if hand.blackjack: 
                profits += 1.5*bet
                if verbose: print('Pocket %s wins %s for blackjack against dealer non-blackjack'%(hand.n,1.5*bet))
            
            # if bust, lose
            elif hand.bust:
                profits -= bet
                if hand.double:
                    profits -= bet
                    if verbose: print('Pocket %s doubled and bust for loss of %s'%(hand.n,2*bet))
                elif verbose: print('Pocket %s bust for loss of %s'%(hand.n,bet))
            
            # surrendered hands lose 0.5x
            elif hand.surrender:
                profits -= 0.5*bet
                if verbose: print('Pocket %s surrenders for loss of %s'%(hand.n,0.5*bet))
            
            # if dealer bust or hand beats dealer value, win
            elif table[-1].bust or hand.value > table[-1].value:
                profits += bet
                if hand.double:
                    profits += bet
                    if verbose: print('Pocket %s doubled and won %s'%(hand.n,2*bet))
                elif verbose: print('Pocket %s won %s'%(hand.n,bet))
            
            # if hand loses to dealer value, lose
            elif hand.value < table[-1].value:
                profits -= bet
                if hand.double:
                    profits -= bet
                    if verbose: print('Pocket %s doubled and lost %s'%(hand.n,2*bet))
                elif verbose: print('Pocket %s lost %s'%(hand.n,bet))
            
            # otherwise, standoff
            elif verbose: print('Pocket %s push'%(hand.n))
    
    if verbose: print('')
        
    # collect all hands
    dealt = []
    for hand in table: dealt += hand.hand
    return profits,bets,dealt


# initialise deck
deck = CSM(decks,buffer)
print('[%s] initialising CSM with %s decks and buffer %s. forced count: %s'%(datetime.datetime.now().replace(microsecond=0),decks,buffer,'%s to %s'%(c[0],c[-1]) if len(c) > 1 else c[0]))

edge_by_count = {i:None for i in c}
for fc in c:
    if len(c) > 1: print('[%s] beginning simulations with forced count %s'%(datetime.datetime.now().replace(microsecond=0),fc))
    
    # global stats initialisation
    count_stats = {i:[0,0,0] for i in range(-10,16)}
    winning_rounds, losing_rounds, even_rounds = 0,0,0
    all_bets, all_profits = 0,0
    lowest_negative, highest_positive = 0,0
    winning_streak, losing_streak, longest_winning_streak, longest_losing_streak = 0,0,0,0
    profit_stats = []

    count = 0
    for i in range(n):
        # set forced count
        if fc != None: 
            deck.set_count(fc)
            count = fc
        
        # set betting strat
        if len(strat) == 4: pockets,bet = 3 if count <= strat[0] else 5,strat[1] if count <= strat[2] else strat[1]*strat[3]*count
        else: pockets,bet = strat
            
        # play a round
        profits,bets,dealt = play_one_round(pockets,bet,deck,count,verbose=bool(args.V),deviate=bool(args.d))
        
        # update global stats        
        if count <= -10: 
            count_stats[-10][0] += 1
            count_stats[-10][1] += profits
            count_stats[-10][2] += bets
        elif count >= 15: 
            count_stats[15][0] += 1
            count_stats[15][1] += profits
            count_stats[15][2] += bets
        else: 
            count_stats[count][0] += 1
            count_stats[count][1] += profits
            count_stats[count][2] += bets
        
        if profits > 0: 
            winning_rounds += 1
            if losing_streak:
                losing_streak = 0
                winning_streak = 1
            else: winning_streak += 1
        elif profits < 0: 
            losing_rounds += 1
            if winning_streak:
                winning_streak = 0
                losing_streak = 1
            else: losing_streak += 1
        else: 
            even_rounds += 1
            winning_streak, losing_streak = 0,0

        if winning_streak > longest_winning_streak: longest_winning_streak = winning_streak
        if losing_streak > longest_losing_streak: longest_losing_streak = losing_streak
        all_profits += profits
        all_bets += bets
        if all_profits < lowest_negative: lowest_negative = all_profits
        if all_profits > highest_positive: highest_positive = all_profits

        profit_stats.append(all_profits)
        
        # update count and restore dealt cards
        count = get_count(dealt)
        deck.restore(dealt)

        if i and not i%report: print('[%s] %s/%s rounds done. estimated house edge: %s%%'%(datetime.datetime.now().replace(microsecond=0),i,n,-round(100*all_profits/all_bets,2)))

    if len(c) > 1:
        edge = -all_profits/all_bets
        print('[%s] finished %s simulations with forced count %s. house edge: %s'%(datetime.datetime.now().replace(microsecond=0),n,fc,edge))
        edge_by_count[fc] = edge
        
    
if not args.V: print('[%s] done!\n'%(datetime.datetime.now().replace(microsecond=0)))    
print('===== RESULTS =====')

if args.V:
    print('total bets: %s'%all_bets)
    print('total profit: %s'%all_profits)
elif len(c) > 1:
    for i in c: print('house edge at forced count %s: %s%%'%(i,edge_by_count[i]))
    res = edge_by_count
elif args.T:
    for i in range(-10,16): print('transition probability to count %s: %s%%'%(i,count_stats[i][0]/n))
    res = count_stats
else:
    res = profit_stats
    edge = -all_profits/all_bets
    
    print('MONEY')
    print('Total bets: %s'%all_bets)
    print('Total profit: %s'%all_profits)
    print('Estimated house edge: %s (%s%%)'%(edge,round(edge*100,2)))
    print('Lowest negative profit: %s'%lowest_negative)
    print('Highest positive profit: %s'%highest_positive)

    print('\nROUNDS STATS')
    print('Number of rounds: %s'%n)
    print('Profitable rounds: %s (%s%% of rounds)'%(winning_rounds,round(100*winning_rounds/n,2)))
    print('Losing rounds: %s (%s%% of rounds)'%(losing_rounds,round(100*losing_rounds/n,2)))
    print('Even rounds: %s (%s%% of rounds)'%(even_rounds,round(100*even_rounds/n,2)))
    print('Longest winning streak: %s'%longest_winning_streak)
    print('Longest losing streak: %s'%longest_losing_streak)

    print('\nCOUNT STATS')
    for i in range(-10,16):
        if count_stats[i][0]: print('%s: %s rounds (%s%%), profit %s (estimated ev %s%%)'%(i,count_stats[i][0],round(100*count_stats[i][0]/n,2),count_stats[i][1],round(100*count_stats[i][1]/count_stats[i][2],2)))


if args.o:
    try: 
        with open(args.o,'w') as f: f.write(str(res))
    except: print('[%s] error writing to outfile. printing results to console\n\n%s'%(datetime.datetime.now().replace(microsecond=0),res))

