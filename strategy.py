import json
import os

STRATS = 'strats.json'
# Strats must have:

def read_strat():
    """
    reads and returns strat from json. Also processes strats filling in nan values with appropriate values 
    """
    try:
        with open(STRATS, 'r') as f:
            data = json.load(f)
        return data
    except:
        print("Warning: Error in opening strat, returning empty json")
        return {}

def save_strat(strat):
    """
    takes in json of the strat and saves it
    """
    os.remove(STRATS)
    with open(STRATS, 'w') as f:
        json.dump(strat, f, indent=4)

def proofread_strat(strats):
    """
    proofreads strat and makes sure everything is in agreement, no contradictions in the json file
    ie, if all strats have -1, then change file to finished
    """
    if strats['pair']: #Not empty
        strats['finished'] = 0 if (False in list(map(lambda x: strats['pair'][x]['pos']==-1, strats['pair']))) else 1
    else: strats['finished'] = 1
    if strats['finished']: strats['long'] = None
    return strats

def json_editor():
    """
    if ran as a script, provides terminal interface to edit strats
    """
    active = True
    while active:
        strats = read_strat()
        cmd = input("Type [v] to view all strats, [a] to add strat, [d] to delete strat, [i] to init strats, [q] to quit\n")
        if (cmd.lower() == "v"): view_all_strats(strats)
        elif (cmd.lower() == "i"): init_strats(strats)
        elif (cmd.lower() == "a"): add_strat(strats)
        elif (cmd.lower() == "d"): delete_strat(strats)
        elif (cmd.lower() == "q"): active = False
        else: print("Invalid command...")

def init_strats(strats):
    """
    properly inits strat to have bare minimum if given empty file, else ignores file
    """
    try: strats['finished']
    except: strats['finished'] = 0
    try: strats['long']
    except: strats['long'] = None
    try: strats['leverage']
    except: strats['leverage'] = 0.9
    try: strats['pair']
    except: strats['pair'] = {}
    try: strats['portfolio']
    except: strats['portfolio'] = []
    try: strats['api_quotas']
    except: strats['api_quotas'] = []
    save_strat(strats)

def view_all_strats(strats):
    """
    views all strats. Throws errors if not properly initalized
    """
    print("="*60)
    print(f"Finished = {strats['finished']}")
    print(f"Long     = {strats['long']}")
    print(f"Leverage = {strats['leverage']}")
    for strat in strats['pair']:
        info = strats['pair'][strat]
        print("~"*60)
        print(f"{strat}: pos = {info['pos']}         leverage = {info['leverage']}")
        print("Keywords:")
        for keyword in info['keywords']:
            print(f"- {keyword}")

        print(f"tp:     pos = {info['tp']['pos']}         pct = {info['tp']['pct']}           amt = {info['tp']['amt']}")
        print(f"sl:     pos = {info['sl']['pos']}         pct = {info['sl']['pct']}")
        print(f"early:  pos = {info['early']['pos']}         time = {int(info['early']['time']/60)} min         amt = {info['early']['amt']}")
        print(f"late:   pos = {info['late']['pos']}         time = {int(info['late']['time']/60)} min")

def add_strat(strats):
    """
    prompt user to add a strat and saves
    """
    asset = str(input("Enter name of asset to long (ie BTCUSDT)\n")).upper()
    keywords = []
    while True:
        word = str(input("Enter a keyword. [q] to finish. [r] to restart\n")).lower()
        if word=="q": break
        if word=="r": keywords = []
        else:
            keywords.append(word)
            print(f"Keywords: {keywords}")
    tp_pct = float(input("Enter take profit price multiple (default 1.05)\n"))
    tp_amt = float(input("Enter take profit amount (default 0.3)\n"))
    sl_pct = float(input("Enter stop loss price multiple (default 0.995)\n"))
    early_time = int(input("Enter whole minutes for early time-stop (default 60)\n"))*60
    early_amt = float(input("Enter early time-stop amount (default 0.5)\n"))
    late_time = int(input("Enter whole minutes for late time-stop (default 180)\n"))*60
    leverage = int(input("Enter int amount of leverage to use (default 20)\n"))

    tp = {'pos':0, 'pct':tp_pct, 'amt':tp_amt}
    sl = {'pos':0, 'pct':sl_pct}
    early = {'pos':0, 'time':early_time, 'amt':early_amt}
    late = {'pos':0, 'time':late_time, 'amt':1.0}
    strats['pair'][asset] = {'pos':0, 'leverage':leverage, 'keywords':keywords, 'tp':tp, 'sl':sl, 'early':early, 'late':late}
    strats['finished'] = 0
    save_strat(strats)
    print(f"{asset} strat successfully added")



def delete_strat(strats):
    """
    prompts user to delete a strat and saves
    """
    strat = str(input("Enter name of strat to delete. [q] to quit. [v] to view all strats first\n")).lower()
    if strat=="q": return
    if strat=="v": view_all_strats(strats)
    strat = strat.upper()
    if strat in strats['pair']:
        if str(input(f"Are you sure you want to delete {strat}? [Y] to continue\n"))=="Y":
            if strats['long'] == strat: strats['long'] = None
            del strats['pair'][strat]
            print(f"Successfully deleted strat {strat}")
        else: 
            print(f"Continuing...")
    else:
        print(f"Strat {strat} does not exist")

    strats = proofread_strat(strats)
    save_strat(strats)

if __name__ == "__main__":
    json_editor()












