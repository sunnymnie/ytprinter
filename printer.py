from strategy import read_strat
import youtube_checker as yc
import portfolio_manager as pm
# import trader

def main():
    # Update STRATS
    print("Starting printer...")
    strats = read_strat()
    while strats["finished"] == 0:
        print("Waiting for post...")
        strats = yc.await_for_post(strats)
        print(f"Now trading {strats['long']}...")
        # strats = trader.trade(strats)
        strats = pm.manage_position(strats)
        print("Finished trading...")
    print(f"Printer finished successfully")








if __name__ == "__main__":
    main()
