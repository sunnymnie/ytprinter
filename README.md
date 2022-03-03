# YTPrinter

Python cryptocurrency trading algorithm. Uses Youtube API to get notification of video publishing, then goes long with futures on Binance.

Disclaimer: This strategy is risky. I used it to make money, but I am retiring this strategy due to more profitable strategies.  

## Summary of how program works
1. Set up algorithm and wait for crypto Youtuber to post video
2. When video is posted:
  1. Liquidate all assets in Binance cross margin account
  2. Transfer to Binance futures, goes long with futures
  3. Liquidation set by criteria set beforehand
3. Transfer funds back to Binance cross margin account, re-purchase previously liquidated assets maintaining correct ratio.

## Statistics/Facts
- Can reliably liquidate margin portfolio and go long futures within 3 seconds of detecting video with Youtube api
- Uses threadpools to liquidate batch orders
- Does not use maker orders, everything is monitored in real-time

## How I used this algorithm profitably, and why it probably wouldn't work for you
- I used small amounts of collateral (~$300), and thus my leveraged position usually is less than $10,000, thus the effects of slippage were minimal
- I used 20x leverage with a take profit of 1% and a 0% stop loss. This is possible because for every trade I've backtested (~20), the price is always above your buy price after 1 minute of video publishing. Theoretically the maximum loss given 0% stop loss is just your trading fees + slippage, which if you're going high leverage with futures can amount to a couple of percent if you're not careful.
- When I used this algorithm, the cryptocurrency market was in a relative neutral position where the retail crowd was still active. Now, things have cooled down considerably. Recommended use (if it's ever recommended) is during euphoric stages in bull-markets.
- Beware of using this algorithm during 'falling-knife moments'. Should be self-explanatory, no one youtube video is going to stop an alt-coin from crashing if BTC is falling 10%.

## Risks
- Because everything is monitored in real-time, if program goes offline (internet outage, etc), you'll have an open high-leverage position without proper stop-loss or take-profits
- Algorithm is not tested with leverage >20x, nor high overall trade sizes >$10,000.
- Requires use of multiple Youtube APIs which is against ToS. Can use just one but may miss some videos.
- Few trades / week and small back-testing sample. You can get killed via one trade if you're not careful.
- Yes there's bugs, and no I did not fix them

## How to use
If you want to use this algorithm, please make sure to understand the code first and tailor it to your situation. This project started off as a simple script and evolved much bigger, and everything is very tailored to my situation with hard-coded urls, etc.

### My recommended steps
1. Reach out to me I'll gladly to explain how everything works, what the bugs are, etc
2. Make a folder called `api-keys` and make a file `api-keys.txt`
In `api-keys.txt`, enter your api details in the format:
```
{"binance": {"api":"1d...wP", "secret":"ea...Gi"},
"youtube":{"api":["AI...po",
                    "AI...iK",
                    ...,
                    "AI...Yv"]}}
```
3. Use `strategy.py` to modify `status.json` to suit your situation. Delete trades, add future trades, the leverage to use, the tp/sl, etc. There's a bug with trailing tp/sl, so don't use that.
4. Run the program with `python3 printer.py` and wait for a video to be posted.

Again: there are bugs in my code, you'll likely lose your money if you don't know what you're doing, especially trading high leverage with cryptocurrency futures with a stranger's code.

## Back-of-the-napkin documentation
`printer.py` is the main program, it uses `youtube-checker.py` to wait for a video. If a new video is detected, it checks if the keywords in the title is a valid trade set in `strats.json`. If it is, `printer.py` delegates the work to `portfolio_manager.py` to liquidate existing cross-margin account, transfer to Binance futures, go long pre-determined leverage on specified asset. From there it checks every second if it needs to update tp/sl via rules specified in `strats.json` for the specified trade and if tp/sl has been met, etc, by checking latest price.

Use `tick-data.ipynb` to check back-testing results with tick-data. 
