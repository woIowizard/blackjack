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
A card-counting-based betting strategy involves varying bets such that the player bets more aggressively when the count entails a favourable edge. To formulate such a strategy, we seek to know how the house edge varies with count. In addition, it turns out that for a CSM with small buffer size, the house edge also depends on the number of pockets played (since a larger number of pockets runs out the buffer more quickly, increasing the proportion of cards in a round not affected by the count). The following command runs, for each of the 26 possible count values from -10 to +15, a simulation of 5M rounds with 1 pocket each, resetting the deck to the target count value after each round:

```blackjack -n 5M -p 1 -c A```

The results are as follows:

|Count|1 pocket|2 pockets|3 pockets|4 pockets|5 pockets|
|---|---|---|---|---|---|
|-10|0.00994066872522887|0.00906049815895536|0.010903819496784251|0.0075887719921748625|0.005945398695516308|
|-9|0.009248761787154614|0.00856781205314523|0.010562591168740313|0.007459361678027633|0.005707865374122695|
|-8|0.007519810075717198|0.008257848362206758|0.009169675290686196|0.007196399788861663|0.005271171383003548|
|-7|0.007216943548658794|0.008134476813796983|0.008202246690143983|0.007081912444638871|0.0049926208769952955|
|-6|0.0061815451425469535|0.007069331516574062|0.007616956617500854|0.006140640662547221|0.004904273599678865|
|-5|0.005421561641010196|0.005871703809407495|0.006814811930572097|0.006073564690198731|0.004713350958876891|
|-4|0.0049465737514518|0.0057817128813427866|0.006717191623118072|0.005807983760576887|0.004531767357204793|
|-3|0.0035710564478636155|0.004498892580040326|0.006662122285136016|0.005032568519194796|0.004371769331504996|
|-2|0.003031661088540082|0.004416758420209416|0.004797083050487015|0.004553492203483922|0.004294915325194144|
|-1|0.002172563220872002|0.0035747599889965377|0.004657037831580172|0.004227939220030406|0.004236452407689186|
|0|0.0017503436572156898|0.0032839682276973184|0.0036253790728193393|0.0038995787440876165|0.00400819823727895|
|1|0.0005362795421797175|0.0025679191477510897|0.003276305688272843|0.0036428361128320614|0.0037918027341684378|
|2|-0.0008680833862761178|0.0019455443027193617|0.002589567869970672|0.003600379064029687|0.003708898109675021|
|3|-0.0011047235118650934|0.0011329010242400518|0.0024678402127659193|0.003229489903832785|0.0036678847496487135|
|4|-0.0015560282249800998|0.0006655745397941576|0.0017725405476669174|0.0028599562805691264|0.0036493602757631345|
|5|-0.003027763909616168|0.00036846913084130064|0.0014747360764874424|0.0026432391646220212|0.003627666104594382|
|6|-0.0033945730002604736|-0.00027988145165558343|0.0008062051460985028|0.0026154935073989015|0.0035636522161200147|
|7|-0.004823597311068861|-0.0008700420107552072|0.0007757728067916418|0.0016354904158950463|0.0035416399765091804|
|8|-0.005778641924954072|-0.00113920002581661|-0.0007971414315791877|0.0017142566308130077|0.003409873699951947|
|9|-0.00659413918779642|-0.0018242902771010805|-0.0010902929803202456|0.0014400698055744429|0.00314851344032793|
|10|-0.007343678850129651|-0.0020363829321124248|-0.0014974100153926297|0.000988551736913766|0.002993111193396823|
|11|-0.007549077529171351|-0.003339783934296084|-0.00225965135183103|0.0009359721417203494|0.0029698237857178|
|12|-0.008983276336604201|-0.0038168307418231144|-0.0027988747917354908|0.000926955420306853|0.002769250976507185|
|13|-0.009368139824911553|-0.004484249231865061|-0.003138324442514168|0.0006466574384574554|0.002751618080345252|
|14|-0.010811942849545512|-0.004820875681446687|-0.003968275015734912|0.0001962330023582169|0.0024224655014291096|
|15|-0.010899512332873545|-0.005464019614031691|-0.0046238337371237665|4.56376668738817e-05|0.002160186894884765|

## Transition probabilities
Besides affecting the house edge in the present round, the number of pockets played also indirectly affects the house edge in the next round, because playing a larger number of pockets in one round increases the probability that a more extreme-valued count would obtain in the next round. To account for this, we seek to know the _transition probabilities_ from number of pockets to counts. The following command runs a simulation of 10M rounds with 1 pocket each, computing the proportion of round that end in each count from -10 to +15

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

  
