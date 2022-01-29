from strategy import read_strat
import youtube_checker as yc
import portfolio_manager as pm
import schedule
import time

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
        pm.init_previous_portfolio(strats)
        print("Finished trading...")

def schedule_turn_on(start = "06:00"):
    """schedules turning on"""
    schedule.every().day.at(start).do(main)
    print(f"Scheduled printer to start at {start}")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    schedule_turn_on()
