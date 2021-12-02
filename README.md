# YTPrinter

## Buy immediately upon Coin Bureau's video launch

## TODO:
- Decouple trader.py to trader.py and portfolio_manager.py.
    - trader: can initialize margin buys/sells, transfers, future trading. 
    - portfolio_manager: calls trader at the right times. Is in charge of logistics and interfacing with strats.json. 
- strats.json: keeps track of current margin portfolio as well. 
- rename youtube_checker to strategy_manager. 
- in strategy_manager, every time api list reaches end, instead of sleeping for x seconds, call portfolio_manager to do update on saving most recent % of portfolio + updating client 

## SMALL TODOs:
- If in portfolio_manager, put try catch on trader, if trader fails, refresh client, fetch state in portfolio_manager (updates strats to be same as information on binance), then calls trader again
- In strategy strats set leverage to use
- In strategy after a strat is submitted, print a summary (max loss, tp, sl, time stops,etc)
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
