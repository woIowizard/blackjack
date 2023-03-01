# blackjack

Scripts to help with formulating a card counting strategy for Blackjack.<br>
* blackjack.py--Run simulations of the game
* stratfind.py--Find a betting strategy with positive expected value, if one exists

<hr />

## Summary

It is well-known that Blackjack can be beaten with card counting. It is also thought that continuous shuffling machines make card counting obsolete by making forthcoming cards less predictable. However, it turns out that CSMs have a mechanical feature that allows for some (albeit limited) degree of card counting. This collection of scripts will help us to determine whether the allowed extent of card counting can be exploited to give the player a positive edge over the house. To test the long term results of various cardplay strategies, blackjack.py simulates Blackjack games at a rate of about 6 million rounds per hour. Given the performance of a cardplay strategy, stratfind.py performs an exhaustive search to find a betting strategy that gives the player a positive edge, if one exists. Using these scripts, we found an overall strategy with an edge of ???% in favour of the player.

<hr />

## Usage

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

A popular method for beating Blackjack involves _card counting_, in which a player keeps track of cards that are dealt so they can infer that some cards are less likely to be dealt at a later time. Continuous shuffling machines hinder counting by limiting the number of cards in each round that are affected by the count to a small buffer. In its default setting, blackjack.py simulates a CSM containing 6 decks and with a buffer size of 7; these parameters can be overwritten with the -D and -B options. 

We will see that with the right strategy, the player may still obtain an edge against a CSM. Our strategy comprises two parts: a betting strategy and a cardplay strategy.

## Count-based edge
A card-counting-based betting strategy involves varying bets such that the player bets more aggressively when the count entails a favourable edge. To formulate such a strategy, we seek to know how the house edge varies with count. Moreover, it turns out that for a CSM with small buffer size, the house edge also depends on the number of pockets played (since a larger number of pockets runs out the buffer more quickly, increasing the proportion of cards in a round not affected by the count). The following command runs, for each of the 26 possible count values from -10 to +15, a simulation of 5M rounds with 1 pocket each, resetting the deck to the target count value after each round:

```blackjack -n 5M -p 1 -c A```

The results are as follows:

|Count|1 pocket|2 pockets|3 pockets|4 pockets|5 pockets|
|---|---|---|---|---|---|
|-10|0.008940668725228869|0.008060498158955359|0.009903819496784252|0.0065887719921748624|0.004945398695516308|
|-9|0.008248761787154614|0.0075678120531452306|0.009562591168740312|0.006459361678027633|0.004707865374122695|
|-8|0.006519810075717198|0.0072578483622067575|0.008169675290686195|0.006196399788861663|0.004271171383003548|
|-7|0.006216943548658794|0.007134476813796982|0.007202246690143984|0.006081912444638871|0.0039926208769952955|
|-6|0.0051815451425469535|0.006069331516574062|0.006616956617500854|0.005140640662547221|0.0039042735996788654|
|-5|0.004421561641010196|0.004871703809407495|0.005814811930572097|0.005073564690198731|0.0037133509588768913|
|-4|0.0039465737514518|0.0047817128813427865|0.005717191623118072|0.004807983760576887|0.003531767357204792|
|-3|0.0025710564478636155|0.003498892580040326|0.005662122285136016|0.004032568519194796|0.003371769331504997|
|-2|0.002031661088540082|0.0034167584202094156|0.0037970830504870153|0.0035534922034839212|0.003294915325194144|
|-1|0.0011725632208720016|0.0025747599889965377|0.003657037831580172|0.003227939220030406|0.003236452407689186|
|0|0.0007503436572156897|0.0022839682276973184|0.0026253790728193393|0.0028995787440876165|0.00300819823727895|
|+1|-0.0015362795421797176|0.0015679191477510897|0.002276305688272843|0.0026428361128320614|0.0027918027341684378|
|+2|-0.0018680833862761178|0.0009455443027193618|0.001589567869970672|0.002600379064029687|0.002708898109675021|
|+3|-0.0021047235118650935|0.00013290102424005166|0.0014678402127659192|0.002229489903832785|0.0026678847496487135|
|+4|-0.0025560282249800998|-0.00033442546020584247|0.0007725405476669174|0.0018599562805691264|0.0026493602757631345|
|+5|-0.004027763909616168|-0.0006315308691586994|0.0004747360764874424|0.001643239164622021|0.002627666104594382|
|+6|-0.004394573000260474|-0.0012798814516555835|-0.0001937948539014972|0.0016154935073989013|0.0025636522161200147|
|+7|-0.0058235973110688614|-0.0018700420107552072|-0.00022422719320835813|0.0006354904158950463|0.0025416399765091804|
|+8|-0.006778641924954072|-0.00213920002581661|-0.0017971414315791877|0.0007142566308130077|0.002409873699951947|
|+9|-0.00759413918779642|-0.0028242902771010805|-0.0020902929803202457|0.00044006980557444284|0.00214851344032793|
|+10|-0.008343678850129651|-0.003036382932112425|-0.0024974100153926297|-0.000011448263086234053|0.001993111193396823|
|+11|-0.008549077529171351|-0.004339783934296084|-0.00325965135183103|-0.00006402785827965067|0.0019698237857178|
|+12|-0.0099832763366042|-0.0048168307418231145|-0.003798874791735491|-0.00007304457969314693|0.001769250976507185|
|+13|-0.010368139824911554|-0.005484249231865061|-0.004138324442514168|-0.0003533425615425447|0.001751618080345252|
|+14|-0.011811942849545513|-0.005820875681446687|-0.004968275015734912|-0.0008037669976417831|0.0014224655014291097|
|+15|-0.011899512332873544|-0.006464019614031691|-0.0056238337371237665|-0.0009543623331261183|0.0011601868948847651|

## Transition probabilities
In addition to affecting the house edge in the present round, the number of pockets played also indirectly affects the house edge in the next round, because playing a larger number of pockets in one round increases the probability that a more extreme-valued count would obtain in the next round. We thus seek to know also the _transition probabilities_ from number of pockets to counts. The following command runs a simulation of 10M rounds with 1 pocket each, computing the proportion of round that end in each count from -10 to +15

```blackjack -p 1 -n 10M -T```

The following are the estimated transition probabilities:

|Count|1 pocket|2 pockets|3 pockets|4 pockets|5 pockets|
|---|---|---|---|---|---|
|-10|2e-07|0.0|1.58e-05|0.0001776|0.0009538|
|-9|3e-07|3.4e-06|8.18e-05|0.0008499|0.0024454|
|-8|1.7e-06|5.76e-05|0.0007973|0.0032678|0.0063846|
|-7|1.14e-05|0.000293|0.0040455|0.0092099|0.0139132|
|-6|0.0001952|0.0039209|0.0131497|0.0206081|0.0261724|
|-5|0.0007254|0.0182804|0.0311982|0.0384534|0.0431496|
|-4|0.0167775|0.045782|0.0567652|0.0615574|0.0634234|
|-3|0.079006|0.0903064|0.0888456|0.0868345|0.0842732|
|-2|0.1206957|0.124291|0.1163087|0.108519|0.1020525|
|-1|0.2262205|0.1588589|0.1356521|0.1222394|0.1126316|
|0|0.1914771|0.158095|0.1381395|0.1245056|0.1145413|
|1|0.1490651|0.1375766|0.1252197|0.1152134|0.1075097|
|2|0.1049809|0.1063467|0.1023405|0.0976128|0.0930583|
|3|0.0605969|0.0720696|0.0753905|0.0756748|0.0749966|
|4|0.030715|0.0431561|0.0500386|0.0540491|0.0561677|
|5|0.0129507|0.0229132|0.0303078|0.0356448|0.0390919|
|6|0.0046089|0.0108602|0.0166425|0.0214998|0.0254701|
|7|0.0014529|0.0045697|0.0084635|0.0121712|0.0156032|
|8|0.000396|0.0017515|0.0039159|0.0063813|0.0089571|
|9|9.15e-05|0.0006037|0.0016556|0.003105|0.0047748|
|10|2.15e-05|0.0001852|0.0006663|0.0014213|0.0024133|
|11|7e-06|5.44e-05|0.0002396|0.0006123|0.0011521|
|12|1.1e-06|1.71e-05|8.01e-05|0.000248|0.0005048|
|13|1e-06|4.9e-06|2.81e-05|9.17e-05|0.0002179|
|14|4e-07|1.6e-06|7.7e-06|3.4e-05|9.23e-05|
|15|1e-07|9e-07|4.2e-06|1.79e-05|4.92e-05|


## Betting strategy

![stratfind-help](img/stratfind-help.png)

![stratfind-use](img/stratfind-use.png)

## Deviations
We'll test the possible profitabily of the following deviations from basic strategy
- split: 10s against 2-9, 10s against 2, 10s against 9, 9s against 7, As against A
- double on: hard 10/11 against 10, hard 9 against 2-9, hard 12 against 2-9, soft 17/18 against 2, soft 17/18 against 7, soft 13/14 against 4, soft 13/14 against 7, soft 19 against 3-6
- surrender on: hard 13 against 10, hard 14/15 against 9, hard 16 against 8, hard 17 against 9/10
- don't split: As against 10, 8s against 9
- don't surrender on hard 14

  
