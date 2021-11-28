import pandas as pd
from strategy import read_strat
import youtube_checker as yc
import trader

def main():
    # Update STRATS
    strats = read_strat()
    while strats["finished"] == 0:
        # there are still some strats that need to be done/awaiting
        # Do code to await. Await will return imediately if position is already long
        strats = yc.await_for_post(strats)
        # Next up is looping checking if price and taking profit if needed
        trader.trade(strats)

        strats = read_strat()
    print(f"Printer finished successfully")








if __name__ == "__main__":
    main()
