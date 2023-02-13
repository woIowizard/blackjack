# blackjack

Scripts to help with formulating a card counting strategy for Blackjack.<br>
* blackjack.py--Run simulations of the game
* stratfind.py--Find a betting strategy with positive expected value, if one exists

<hr />

## Summary

It is well-known that Blackjack can be beaten with card counting. It is also thought that continuous shuffling machines make card counting obsolete by making forthcoming cards less predictable. However, it turns out that CSMs have a mechanical feature that allows for some (albeit limited) degree of card counting. Moreover, cardplay and betting strategies can be formulated to exploit this limited degree of card counting to give the player a positive edge over the house. blackjack.py simulates Blackjack games at a rate of about 6 million rounds per hour, allowing us to test the long term results of various cardplay strategies. Given a cardplay strategy, stratfind.py performs an exhaustive search to find a betting strategy that gives the player a positive edge, if one exists. Using these scripts, we found an overall strategy with an expected value of %0.04.

<hr />

## Options

Run blackjack.py with the -h option to see the available options.

![help](img/help.png)

<hr />

## Simulation

In its default setting, blackjack.py simulates a single round of Blackjack according to the rules [here](https://www.cra.gov.sg/docs/default-source/game-rule-documents/mbs-blackjack-v6.pdf). The simulated player opens 5 pockets with bets of $25 on each, and follows basic strategy. For verbose reporting of the decisions made during the simulated round, run

```blackjack -V```

![verbose](img/verbose.png)

Nothing groundbreaking is happening here. The verbose option just allows you to check my implementation of basic strategy.

<hr />

## Basic strategy

To estimate the house edge over 5 million rounds, run

```blackjack -n 5M```

![standard-edge](img/standard-edge.png)

The results of the simulation come close to known values from [publicly available sources](https://wizardofodds.com/games/blackjack/calculator/).

![known-baseline](img/known-baseline.png)

In what follows, our goal is to formulate a strategy that not only improves (that is, lowers) the house edge, but gives the player a positive edge.

A popular method for beating Blackjack involves _counting_, in which a player keeps track of cards that are dealt so they can infer that some cards are less likely to be dealt at a later time. A high count indicates that low cards are less likely to be dealt, which favours the player; and a low count inversely. Counting strategies recommend varying bets in response to the count such that bets are more aggressive under favourable conditions, and on balance the player makes positive profit despite losing more often than winning. Modern anti-counting measures limit the extent to which extreme count values obtain, but we will see that with the right strategy, the player still has an edge.

Our strategy comprises two parts: a cardplay strategy and a betting strategy.

## Baseline
We consider the cardplay strategy first. Without counting in view, it can be taken for granted that basic strategy is optimum. We'll also consider the profitability of deviations from basic strategy when counts are considered. Before considering deviations, we first establish a baseline by estimating the house edge at each count under basic strategy. The following command runs, for each of the 26 possible count values from -10 to +15, a simulation of 5M rounds, resetting the deck to the target count value after each round:

```blackjack -n 5M -c A```

![baseline-sims](img/baseline-sims.png)

The results are as follows

|Count|House edge|
|---|---|
|-10|0.01205493128652319|
|-9|0.01147341898851317|
|-8|0.010259966327881465|
|-7|0.009603017271760892|
|-6|0.008275734783593303|
|-5|0.007708537005791758|
|-4|0.007284183826849221|
|-3|0.005352097530485474|
|-2||
|-1||
|0||
|+1||
|+2||
|+3||
|+4||
|+5||
|+6||
|+7||
|+8||
|+9||
|+10|-0.005699250328388582|
|+11|-0.006861039478373141|
|+12|-0.00731757958056811|
|+13|-0.008668278035943198|
|+14||
|+15||


## Deviations
We'll test the possible profitabily of the following deviations from basic strategy
- split: 10s against 2-9, 10s against 2, 10s against 9, 9s against 7, As against A
- double on: hard 10/11 against 10, hard 9 against 2-9, hard 12 against 2-9, soft 17/18 against 2, soft 17/18 against 7, soft 13/14 against 4, soft 13/14 against 7, soft 19 against 3-6
- surrender on: hard 13 against 10, hard 14/15 against 9, hard 16 against 8, hard 17 against 9/10
- don't split: As against 10, 8s against 9
- don't surrender on hard 14

