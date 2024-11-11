# blackjack

In this repo are scripts to help with formulating a card counting strategy for Blackjack.<br>
* blackjack.py--runs simulations of the game
* stratfind.py--finds a betting strategy with positive expected value, if one exists

<hr />

## Summary

It is well-known that Blackjack can be beaten with card counting. It is also thought that continuous shuffling machines (CSMs) impede card counting by making forthcoming cards unpredictable. However, it turns out that CSMs have a mechanical feature that allows for some (albeit limited) degree of card counting. We show, using this pair of scripts, that the allowed extent of card counting is exploitable to give the player a positive edge over the house. Blackjack.py simulates Blackjack games at a rate of about 6 million rounds per hour, which allows us to test the long term results of various strategies. Stratfind.py uses an approximate brute-force algorithm to find a betting strategy that gives the player a positive edge. We found a strategy with a theoretical edge of 0.04% in favour of the player, which materialised as a 0.09% profit in an experiment of 10 million rounds.

<hr />

## blackjack.py

In its default setting, blackjack.py simulates a single round of Blackjack according to the rules [here](https://www.gra.gov.sg/docs/default-source/game-rules/mbs/blackjack-pontoon-games/blackjack-pontoon---gra-website/mbs-blackjack-game-rules-version-63c8994ee-f3e8-4bfd-8398-dee76aa466ee.pdf?sfvrsn=3d3481e5_1). The simulated player opens 5 pockets with bets of $25 on each, and follows basic strategy. To see the simulated player's decisions in action, run

```blackjack -V```

![verbose](img/verbose.png)

Run blackjack.py with the -h option to see other available options for overriding the script's default behaviour:

![help](img/help.png)

By simulation, we can verify that basic strategy alone is insufficient to give the player a favourable edge. The following command runs a simulation of 5 million rounds under basic strategy:

```blackjack -n 5M```

![standard-edge](img/standard-edge.png)

The results of the simulation come close to known values from [publicly available sources](https://wizardofodds.com/games/blackjack/calculator/).

![known-baseline](img/known-baseline.png)

In what follows, our goal is to formulate a strategy that gives the player a favourable edge.

<hr />

## Card-counting theory

A popular method for beating Blackjack involves _card counting_, in which a player keeps track of cards that are dealt so they can infer that forthcoming cards are more likely to be in their favour. More precisely, the count at any point is the number of high cards (10 to A) that have been dealt subtracted from the number of low cards (2 to 6) that have been dealt. A high (low) count indicates that forthcoming cards are likely to be high (low), which favours the player (house). Card counting is often used in conjunction with a betting strategy in which the player bets conservatively at low counts and aggressively at high counts, such that the player has an positive overall edge.

The card-counting strategy works best when cards played are not shuffled back into the deck, so that the count reliably reflects the value of forthcoming cards. Continuous shuffling machines (CSMs) falsify this condition by allowing the dealer to shuffle, at the end of each round, the cards dealt in that round back into the deck. In theory, this would prevent card counting, since it seems to entail that likelihood of high cards being dealt in any round is independent of the cards played in the previous round. In practice, however, CSMs smoothen dealing by maintaining a small _buffer_ of cards that are not shuffled when cards are fed into the CSM. The count in a given round is thus a reliable guide to the likelihood of high cards coming from that buffer. It turns out that this degree of card counting, despite being extremely limited compared to the traditional method, is sufficient to formulate a strategy that gives the player a favourable edge.

In its default setting, blackjack.py implements a CSM containing 6 decks and with a 7-card buffer, which matches the apparent specifications of the CSM used in the casino at Marina Bay Sands. These parameters can be overridden with the -D and -B options.

<hr />

## Strategy formulation

To formulate a strategy, we require to know how the house edge varies with the count. In addition, it turns out that for CSMs with a small buffer, the house edge also depends on the number of pockets played (since a larger number of pockets runs out the buffer more quickly, increasing the proportion of cards in a round not indicated by the count). Using blackjack.py, we ran simulations of 5 million rounds at each number of pockets from 1-5, and each count value from -10 to +15. For example, the following command runs, for each of the 26 possible count values from -10 to +15, a simulation of 5M rounds with 1 pocket each, resetting the deck to the target count value after each round:

```blackjack -n 5M -p 1 -c A```

The per-count estimated house edges are as follows:

|Count|1 pocket|2 pockets|3 pockets|4 pockets|5 pockets|
|---|---|---|---|---|---|
|-10|0.00844066872522887|0.00756049815895536|0.009403819496784252|0.006088771992174863|0.0044453986955163075|
|-9|0.007748761787154614|0.007067812053145231|0.009062591168740313|0.005959361678027632|0.0042078653741226945|
|-8|0.006019810075717199|0.006757848362206758|0.007669675290686196|0.005696399788861663|0.003771171383003548|
|-7|0.005716943548658794|0.006634476813796983|0.006702246690143984|0.0055819124446388705|0.0034926208769952955|
|-6|0.004681545142546954|0.005569331516574062|0.006116956617500854|0.004640640662547222|0.0034042735996788654|
|-5|0.003921561641010197|0.004371703809407495|0.005314811930572098|0.00457356469019873|0.003213350958876891|
|-4|0.0034465737514518|0.004281712881342787|0.005217191623118072|0.0043079837605768875|0.0030317673572047925|
|-3|0.0020710564478636155|0.0029988925800403256|0.005162122285136015|0.003532568519194796|0.0028717693315049963|
|-2|0.001531661088540082|0.0029167584202094156|0.0032970830504870153|0.0030534922034839217|0.002794915325194144|
|-1|0.0006725632208720018|0.0020747599889965377|0.003157037831580172|0.002727939220030406|0.002736452407689186|
|0|0.00025034365721568973|0.0017839682276973184|0.0021253790728193393|0.0023995787440876165|0.00250819823727895|
|1|-0.0009637204578202825|0.0010679191477510896|0.001776305688272843|0.0021428361128320614|0.0022918027341684378|
|2|-0.002368083386276118|0.0004455443027193617|0.001089567869970672|0.002100379064029687|0.002208898109675021|
|3|-0.0026047235118650935|-0.00036709897575994827|0.0009678402127659192|0.001729489903832785|0.0021678847496487135|
|4|-0.0030560282249801|-0.0008344254602058425|0.0002725405476669174|0.0013599562805691264|0.0021493602757631344|
|5|-0.004527763909616168|-0.0011315308691586994|-2.5263923512557638e-05|0.0011432391646220212|0.002127666104594382|
|6|-0.004894573000260473|-0.0017798814516555835|-0.0006937948539014972|0.0011154935073989015|0.0020636522161200147|
|7|-0.006323597311068862|-0.002370042010755207|-0.0007242271932083582|0.0001354904158950463|0.0020416399765091804|
|8|-0.007278641924954072|-0.00263920002581661|-0.0022971414315791877|0.00021425663081300764|0.001909873699951947|
|9|-0.00809413918779642|-0.0033242902771010805|-0.0025902929803202457|-5.9930194425557174e-05|0.0016485134403279298|
|10|-0.008843678850129651|-0.003536382932112425|-0.0029974100153926297|-0.0005114482630862341|0.001493111193396823|
|11|-0.009049077529171352|-0.0048397839342960835|-0.00375965135183103|-0.0005640278582796506|0.0014698237857178002|
|12|-0.0104832763366042|-0.005316830741823115|-0.004298874791735491|-0.000573044579693147|0.001269250976507185|
|13|-0.010868139824911553|-0.005984249231865061|-0.004638324442514169|-0.0008533425615425447|0.001251618080345252|
|14|-0.012311942849545511|-0.006320875681446687|-0.0054682750157349115|-0.001303766997641783|0.0009224655014291095|
|15|-0.012399512332873544|-0.00696401961403169|-0.006123833737123767|-0.0014543623331261183|0.0006601868948847649|

In contrast to the legacy shuffling system, in which the house edge at a count is independent of the number of pockets played, we observe that with a CSM, some count admit player-favourable edges at low pocket numbers but not high pocket numbers. This phenomenon is expected, for reasons given above, and must be accounted for because it limits how aggressive a betting strategy can be in terms of the number of pockets it plays.

Besides affecting the house edge in the present round, the number of pockets played also indirectly affects the house edge in the next round, because playing a larger number of pockets in one round increases the probability that a more extreme-valued count would obtain in the next round. To account for this, we seek to know the _transition probabilities_ from number of pockets to counts. That is, for each number of pockets from 1-5, we seek the probability that a round played with that number of pockets will end in a particular count value. (We assume for now that the cardplay strategy does not change with the count, so that the starting count value is unimportant. This assumption will become false later, but should not affect the results here too much.) The following command runs a simulation of 10 million rounds with 1 pocket each, reporting the proportion of rounds that end in each count from -10 to +15

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

Using these data, we can formulate a favourable betting strategy with stratfind.py. The script takes as input two matrices containing the per-count edges and transition probabilities, and runs an approximate brute-force algorithm to find a betting strategy that gives the player an edge above a specified threshold. The strategy to be identified has the following form<br>
(i) if at a particular count, the player does not have positive edge at any number of pockets, bet the minimum and play a number of pockets to be determined between 1-5<br>
(ii) if at a particular count, the player can attain positive edge for some number of pockets, play the number of pockets that maximises the player's edge and bet x*minimum*c, where c is the count and x is a natural number to be determined.<br>
This betting strategy follows the typical pattern for card-counting strategies: conservative at unfavourable counts and aggressive at favourable counts. 

To improve the robustness of our results against random error in the trials above, we adjust the edge values by .0015 in favour of the house, thus forcing stratfind to find a strategy that favours the player even under possible handicap. In its default setting, stratfind takes the minimum to be $25, searches upward from x=1 without limit, and seeks a strategy with positive edge. These can be overridden with command-line options

![stratfind-help](img/stratfind-help.png)

Given the matrices above, a full brute-force search would take considerable time (5^12 > 200M trials for each value of x). Stratfind in its default setting thus does only an approximate brute-force search in which the number of pockets at odd-valued counts are assumed to be identical to those at the immediately-lower count--this can be overridden with the -F option. The approximation reduces the search space to 15625 trials at each value of x, which can be performed in below 5 seconds. Running `stratfind` without options begins the search:

![stratfind-first](img/stratfind-first.png)

Stratfind finds that a positive edge of 0.0116% is possible at x=2. Given the wide possible variation in results, we might seek a yet more robust edge. The following command runs a brute-force search beginning at x=3 and sets the threshold to 0.02%:

```stratfind -s 3 -b .0002```

![stratfind-second](img/stratfind-second.png)

A strategy of edge 0.0444% is possible at x=3. Given the uniformity of pocket numbers from counts -10 to +1, a full brute force search seems unnecessary. Our strategy is hence as follows:
- at counts +12 and below, play 1 pocket; at counts +13 and above, play 3 pockets
- at counts +1 and below, bet $25; at counts +2 and above, bet $75*count

<hr />

## Validation
Running blackjack.py with the -S option implements this strategy. As validation, we run a simulation of 10 million rounds:

```blackjack -n 10M -S```

![betstrat-confirm](img/validation.png)

We observe from the results that the player came out with a .09% profit. Moreover, the profit margin was positive (albeit with some fluctation) at every intermediate point taken at 1 million round intervals, indicating the stability of this result. It may also be observed that there were significantly more losing rounds than profitable rounds, with 42% of rounds being profitable and 50% of rounds losing. Nevertheless, the profitable rounds at favourable counts (>= +2) returned gains that outweighed the losses from losing rounds, hence the overall favourable edge. This is typicaly of card counting strategies. Hence, we have used card counting to beat Blackjack, even in the presence of a continuous shuffling machine. 


<hr />

## Cardplay strategy

Presumably, basic strategy represents the optimal count-insensitive cardplay strategy. With counting in view, however, it might be advantageous to deviate from basic strategy at certain count ranges. We will test the possible profitability of the following deviations from basic strategy:
- split: 10s against 2-9, 10s against 2, 10s against 9, 9s against 7, As against A
- double on: hard 10/11 against 10, hard 9 against 2-9, hard 12 against 2-9, soft 17/18 against 2, soft 17/18 against 7, soft 13/14 against 4, soft 13/14 against 7, soft 19 against 3-6
- surrender on: hard 13 against 10, hard 14/15 against 9, hard 16 against 8, hard 17 against 9/10
- don't split: As against 10, 8s against 9
- don't surrender on hard 14

Given the large number of possible deviations, it seemed impractical to run large numbers of simulations for each count value for each possible deviation. To narrow in on a shortlist of viable deviations, we first ran smaller simulations of 3 million rounds at counts -10, 0, and +15 for each possible deviation (under the above betting strategy). The following command runs such a test:

```blackjack -S -n 3M -c B -d```

The observed house edges are as follows:

|Deviation|-10|0|+15|
|---|---|---|---|
|Baseline|0.00844066872522887|0.0002503436572156898|-0.0061238337371237665|
|Split 10 against 2-9|0.013291908320854213|0.005599867417652645|-0.0008497423705041022|
|Split 10 against 2|0.009530636311391599|0.0011388145589275008|-0.005635645438571812|
|Split 10 against 9|0.009497115787199983|0.0011595819239482534|-0.003299006574022928|
|Split 9 against 7|0.008968004445809004|0.00004165253366838492|-0.005217902365448402|
|Split A against A|0.009234368239258111|-0.0005092892628557069|-0.005954250808266156|
|Dbl hard 10/11 against 10|0.009749837155775643|0.0014851885113143538|-0.0034680611469492927|
|Dbl hard 9 against 2-9|0.010934469612335861|0.001674240859937675|-0.005126565592279925|
|Dbl hard 12 against 2-9|0.020599380581904043|0.012610972920445416|0.007434395571377581|
|Dbl soft 17/18 against 2|0.009811489276123552|-0.00026137721924476305|-0.005837186307166255|
|Dbl soft 17/18 against 7|0.010153213695494694|0.0006417709656370583|-0.005037812970377555|
|Dbl soft 13/14 against 4|0.008283740657402009|0.00150270570568689|-0.0063721165400529595|
|Dbl soft 13/14 against 7|0.009762139897977563|0.00022239411817525254|-0.004714093812550419|
|Dbl soft 19 against 3-6|0.009088376463477687|0.0005029222208521054|-0.005199264113716582|
|Sur hard 13 against 10|0.010147023736308684|0.0007043227848271481|-0.005054234181881401|
|Sur hard 14/15 against 9|0.009087620339416931|0.0011588075952030296|-0.005425400925886805|
|Sur hard 16 against 8|0.009215766613310201|0.0012636471652007562|-0.005051336288757243|
|Sur hard 17 against 9/10|0.010629687400474905|0.0013453087622531995|-0.005366145899500477|
|Don't split A against 10|0.009117781558429919|0.000580702014856393|-0.004191916982545506|
|Don't split 8 against 9|0.00865102995793827|0.0003763750699441553|-0.006012085878571659|
|Don't surrender hard 14|0.00923402482594167|-0.0007080942643767037|-0.00641383428800706|

Based on this rough estimate, the viable deviations are:
- split 9 against 7
- split A against A
- double soft 17/18 against 2
- double soft 13/14 against 4
- double soft 13/14 against 7
- don't surrender hard 14

The other possible deviations did not show significant improvements from basic strategy at either low, high, or middling counts, and thus did not warrant further investigation. We did more thorough tests of the shortlisted viable deviations, running simulations of 3 million rounds at each count from -10 to 15. The following command runs the test

```blackjack -S -n 3M -c A -d```

The per-count edges for each viable deviation are as follows:

|Count|Baseline|split 9 against 7|split A against A|dbl soft 17/18 against 2|dbl soft 13/14 against 4|dbl soft 13/14 against 7|don't surrender hard 14|
|---|---|---|---|---|---|---|---|
|-10|0.00844066872522887|0.009657596850588606|0.008718126257350866|0.009675799425718909|0.009354105381701028|0.009990470896294892|0.008759485269498692|
|-9|0.007748761787154614|0.007359651486172107|0.008417653677997839|0.008540384851628908|0.007632994388562369|0.008686323315325217|0.00951469848177024|
|-8|0.006019810075717199|0.007193703562512701|0.006965988138592186|0.008040465885686807|0.007489446224646933|0.007193497390095847|0.007442284010071452|
|-7|0.005716943548658794|0.006035230950170299|0.005471165794712306|0.006392127348712934|0.00667960235795671|0.005607522645251237|0.005350711611376871|
|-6|0.004681545142546954|0.005631189277571219|0.005392433468644626|0.004999262413637838|0.005459963434974761|0.005936451127551793|0.004786956283841008|
|-5|0.003921561641010197|0.0046883221294455775|0.004216295152859853|0.005648875824546342|0.004587928989862064|0.004650520975990008|0.0039928337872470335|
|-4|0.0034465737514518|0.0031837795873752594|0.004135093312418917|0.002939067738117249|0.004093110799889388|0.0038996087459446894|0.0030911654868537256|
|-3|0.0020710564478636155|0.0020844182687919767|0.002269243633150721|0.004776888144177766|0.0029293660916054794|0.0032748375453197517|0.0025679341263627523|
|-2|0.001531661088540082|0.0019635679056658004|0.0014719705319610847|0.0018879507134210852|0.0019828269170057006|0.0023748038493622667|0.002091176176557042|
|-1|0.0006725632208720018|0.0009096217401238615|0.0004883532525341534|0.0017561507750222425|0.002086781126700874|0.0020585171463614184|0.0008175316039563991|
|0|0.00025034365721568973|-0.0005330241882700608|0.0004908052822302192|-0.0006457751688262104|-4.2218125389920934e-05|0.0009549409878992074|0.0006478104753120698|
|1|-0.0009637204578202825|-0.000683784254875134|-0.001320247996244256|-0.0016114444344944928|-0.0007212662534828626|-0.0009745814821757553|0.0009836835344416348|
|2|-0.002368083386276118|-0.0013614563364708755|-0.001211948278641625|-0.0024073546341950103|-0.0013831905236289447|-0.0010539638452306008|-0.0012654122060063544|
|3|-0.0026047235118650935|-0.0024056315587713834|-0.0012341251392413476|-0.0030141309153720527|-0.0020159084427507114|-0.002168171805904004|-0.001809256905500153|
|4|-0.0030560282249801|-0.0029657975415130836|-0.0034712372713561895|-0.0024633768797625013|-0.0025561330284467995|-0.0020731469799727927|-0.0026749080945149177|
|5|-0.004527763909616168|-0.004008825650250342|-0.004938040311267251|-0.002921379518382366|-0.0037738537521661416|-0.00299645563131859|-0.0038815534847941135|
|6|-0.004894573000260473|-0.005265602153371344|-0.005536154918758771|-0.005152236679683674|-0.003751342171824949|-0.003595386763885366|-0.003887188123220923|
|7|-0.006323597311068862|-0.005272609165932818|-0.005498684343613972|-0.0063754367594494234|-0.005339184494423112|-0.0054649345604583675|-0.005562066603668148|
|8|-0.007278641924954072|-0.006583349651550992|-0.006552797512174522|-0.006293457826231661|-0.006606794745889394|-0.005308227445168708|-0.005970385660855526|
|9|-0.00809413918779642|-0.007763913092736321|-0.006828045540340711|-0.00868338346372235|-0.00762401309726714|-0.0070337419170930044|-0.0073947377122605355|
|10|-0.008843678850129651|-0.008608225006093454|-0.008345139278077503|-0.00784857031513174|-0.00725949296938899|-0.007351949744159236|-0.007571548864613761|
|11|-0.009049077529171352|-0.009058361866864784|-0.008446658812296405|-0.008887292312333645|-0.008970607196021052|-0.008847412817262049|-0.008569858807237258|
|12|-0.0104832763366042|-0.009420159372914795|-0.010742703972532602|-0.00914242828502201|-0.008546097157467288|-0.009781294218178997|-0.008095592695869886|
|13|-0.004638324442514169|-0.004429890362372543|-0.004813623166605195|-0.004270810372930756|-0.0046461722546595145|-0.0038253112860975576|-0.004844969515120273|
|14|-0.0054682750157349115|-0.004920584473516753|-0.004764577596430223|-0.005429666087455441|-0.004500599387333098|-0.004366393292507006|-0.005577021214551287|
|15|-0.006123833737123767|-0.006505736265983462|-0.0057997148444618955|-0.005782548573829851|-0.006168052075461693|-0.00475935352985052|-0.005886061481225696|

The results showed significant variance due to the relatively small number of rounds. Nevertheless they seem sufficient to conclude that deviating from basic strategy would not yield significant edge improvements, even with counting in view.


<hr />

## How practical is this?
The results above indicate theoretical long-term profits. In practice, however, time and money constraints might limit the effectiveness of card-counting as a money-making method. To get a sense for how the above strategy might play out in practice, we run 144000 round simulations, corresponding to approximate number of rounds that may be expected to be played in a year (50 weeks x 48 hours/week x 1 round/min). The following command in Powershell runs 100 such simulations:

```foreach ($i in 1..100){echo "===== TRIAL $i =====";blackjack -S -n 144000;echo "";echo ""}```

The raw results from these trials are in practical-trial.txt. A summary of the key findings is as follows:

||profit|lowest negative|highest positive|
|---|---|---|---|
|min|-64000.0|-83512.5|387.5|
|max|150525.0|-425.0|150750.0|
|ave|18166.125|-24644.125|47603.875|

We observe that although the average estimated annual profit is positive, the negative loss can go below -80k, and indeed goes below 50k in 14% of the trials. The average annual profits and highest positive profits also varied quite widely in the trials. So despite the theoretical profitability of the strategy above, it is in practice rather risky as a money-making method.
