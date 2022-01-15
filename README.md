# YTPrinter

## 3-pool-plan 

|Info|Main|Gamble|Reserve|
|---|---|---|---|
|Medium| exodus and trezor/ledger | Binance (margin) and self-custory | Binance (spot) |
|Purpose| Swing-trading, hodling. Copy Coin Bureau's trades| Leverage trading or risky bets | USDT |
|Profits (>$200)| 100% retained | **if reserve < $5000**: 50% retained, 30% main, 20% reserve. **else**: 60% retained, 40% main | **if reserve <$3000**: 100% retained **else if reserve <$5000**: 50% main, 30% retained, 20% gamble **else**: 70% main, 30% gamble |

## Goal/plan
- Jan-30: Switch to using up to 50x 
- Feb21-25 create version 2
    - Adjusts to what is max leverage
    - Buys as much as can in first 10 seconds, in small batches. $2000 at 20x, break even in first minute, liquidate in small batches as well. 
- Apr1: reach $600-$100-$3000: ~$4000
    - Reach enough in reserve to start moving funds to main and gamble
    - Up until this point, reserve and main (binance portion) are the same. Hold BTC/ETH, etc and liquidate to go leveraged futures
- May1: reach $1000-$100-$5000: ~$6000
    - Reach max reserve. Excess earned in Binance is withdrawn. Reserve can still be mostly assets, but aim to permanently hold $1000 in USDT. 
- Aug1: reach $5000-$2000-$5000: ~$12000
    - Assuming minor appreciation. Reserve can still be mostly assets, but aim to permanently hold $2000 in USDT. 
- Nov1: reach $10000-$3000-$5000: ~$18000
    - Assuming some appreciation
- Dec31: reach $35000-$5000-$5000 ~$1BTC ~$43000

## Criterion
- Does Coin Bureau own the coin?
    - +1 if he does not
    - 0 if he does
    - -1 if he recently allocated to the coin
- Is the market crashing?
    - +4 if BTC price fell by >10% with big bottom liquidations
    - +2 if BTC price fell by at most ~10% but no massive market liquidations
    - 0 if seemingly in accumulation/distribution phase or gentle bull market
- Did the coin have a substantial up-moves recently
    - +3 if within the past 3 days the coin made substantial upmoves exceeding 30% and market was stationery or falling
    - +2 if within the past 3 days the coin made substantial upmoves exceeding 15% and market was stationery or falling
    - +1 if coin made upmoves exceeding 15% but market was also going up
    - 0 otherwise
- Is the coin ranked in the top by market cap
    - +2 if within top 10 or 24h volume greater than 10% of BTCUSDT 24h volume
    - +1 if within top 20 or 24h volume greater than 5% of BTCUSDT 24h volume
    - 0 otherwise

0-2: Stop loss + 3ish hour time stop
3-5: Stop loss + 50% take profit at 2%+ 3ish hour time stop
6-8: Stop loss + 100% take profit at 2% + 1ish hour time stop
9+: Do not trade

## Buy immediately upon Coin Bureau's video launch

## TODO:
- add trade price to strats information
- turn hard-coded tp/sl/time stops into a list of critical moments
    - Every critical moment object has
        - a type: time_stop, price_stop. 
        - corresponding trigger price/time
        - an uuid. Just so can easily reference it
        - an amount of portfolio to sell as a float
        - last changed time
        - a list of triggers

- a trigger object:
    - a trigger. Is just a function that takes in current price + time and bought price + last changed time and returns boolean (function pointer)
    - a list of saved paramaters in format [param1, param2, param3]
    - a function pointer (somehow) to do an action at a time or price
        - function takes in the critical moment object, the trigger uuid, the list of paramaters and changes the critical moment correspondinly and returns it
    - an uuid. Just so can easily reference the trigger itself so it can change itself
- a trigger function
    - takes in a critical moment object, a trigger uuid, a list of paramaters. Returns a critical moment object
    - caller function has to take returned critical moment's uuid and find original critical moment and delete it before putting it into the list in strats
    - Some possible trigger functions
        - if price is above buy price by x%, 
An example of how I think it will work in Portfolio manager's POV
```
for cm in critical_moments:
    if cm.liquidate(price and time):
        liquidate(cm.amt, ...)          # Passing in exact amount of futures to liquidate, instead of float. Set when trade is instantiated
        cm.finished = True or something
    else:
        new_cm = cm
        for t in cm.triggers:
            if t.trigger(price + time + bought price + last changed time):
                new_cm = t.func(new_cm, t.uuid, t.params)
        if (new_cm != cm):
            del cm
            critical_moments.append(new_cm)
        
    
```

## New functionality brainstorming:
- futures buy and sells should utilize limit orders / waiting for price to come down for large orders in order to not drive up price. Also look at order book
- migrate holding portfolio to spot portfolio. Reserve cross margin for manual trades involving margin


- in strategy:
    - in a check make sure that every uuid is different, else generate a new one
- strats.json: keeps track of current margin portfolio as well. 
- rename youtube_checker to strategy_manager. 
- in strategy_manager, every time api list reaches end, instead of sleeping for x seconds, call portfolio_manager to do update on saving most recent % of portfolio + updating client 

## SMALL TODOs:
- If in portfolio_manager, put try catch on trader, if trader fails, refresh client, fetch state in portfolio_manager (updates strats to be same as information on binance), then calls trader again
- Discord capabilities. messenger.py

# Past notes:
## Runtime cycle
### 1. Initalize
1. Checking if waiting for CB to post (cross margin account != 0), or what asset is long. Set value to long
- long: bool -- whether currently long (go to (3)) or no position (waiting for CB to post)
- MAIN: What account to park USDT in (ie 1INCHUSDT)
- STRATS: 
    - A dictionary/csv/json pegging keywords to margin account
    - For asset, np.nan, or price bought at, and if active


### 2. Waiting
1. constantly looping over whether CB posted a new video with keywords
2. If so: 
    1. Transfer to pre-set margin account
    2. Buy with max leverage
    3. go to (3), passing in asset to keep track of and price at which it was bought at (save to STRATS)

### 3. Looking to sell
Reads from STRATS to see which strat is active (should only be one, else firt)
1. Set a stop limit SL order if necessary (>$10 of unsecured asset) at 0.5% below buy price (if exists given order), at the most recent stop limit price for this asset if within 3 days (if exists), or as a last resort 0.5% below current price. 
2. Start timer for 1 hour and 3 hours
3. If amount of asset above $10 (still long the position)
    1. If did not sell 5% already: sell if price is above 5% market order for 33% of position
    2. If 1 hour is up, sell 50% or remaming amount (irregardless)
    3. After 3 hours, liquidate everything, go to (4) 
4. ELSE (all liquidated via stop loss): go to (4)
5. If amount of asset <$10 total, then go to (4) 

### 4. Return to normal state
1. Mark STRATS as completed for asset
2. Send USDT to MAIN
3. If STRATS exists strats not touched yet, go to (2), else finish program. 

## Strats
- `finished` if all strats are expended
- `long` either the pair longing or None
- `main` is binance margin account to store USDT when not in use
- `pair[strats['long']]` 
    - ['pos'] is the position of the `long` pair. 0 is default--have not bought, waiting. 1 is have bought and looking to sell. -1 is finished.
    - ['price'] is the buy price   
    - ['tp'] 
        - ['pos'] is 0 if did not take take-profit yet. 1 if already did
        - ['pct'] is take profit level price*(1+pct)
        - ['amt'] is amount of position to take profit. 0.3 == 30%
    - ['sl'] 
        - ['pos'] is 0 if did not take stop-loss yet. 1 if already did
        - ['pct'] is stop-loss level price*(1-pct)
    - ['early'] 
        - ['pos'] is 0 if did not sell early yet, 1 if did sell early
        - ['time'] is time of early time limit
        - ['amt'] is amount to sell 
    - ['late'] 
        - ['pos'] is 0 if did not sell late yet, 1 if did sell late
        - ['time'] is time of late time limit
        - ['amt'] is amount to sell 
    

## Warnings:
- check if it takes time to init a binance client given imports done

## Uhhh
- Centrifuge CFG
- TrueFi TRU
- Goldfinch
- 
