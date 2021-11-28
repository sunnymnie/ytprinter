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
    try: strats['main']
    except: strats['main'] = 'BTCUSDT'
    try: strats['pair']
    except: strats['pair'] = {}
    save_strat(strats)

def view_all_strats(strats):
    """
    views all strats. Throws errors if not properly initalized
    """
    for strat in strats['pair']:
        print(f"{strat}: {strats['pair'][strat]}")

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
    tp = {'pos':0, 'pct':1.05, 'amt':0.3}
    sl = {'pos':0, 'pct':0.995}
    early = {'pos':0, 'time':60*60, 'amt':0.5}
    late = {'pos':0, 'time':3*60*60, 'amt':1.0}
    strats['pair'][asset] = {'pos':0, 'keywords':keywords, 'tp':tp, 'sl':sl, 'early':early, 'late':late}
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
            del strats['pair'][strat]
            print(f"Successfully deleted strat {strat}")
        else: 
            print(f"Continuing...")
    else:
        print(f"Strat {strat} does not exist")

    if strats['pair']: #Not empty
        strats['finished'] = 0 if (False in list(map(lambda x: x['pos']==-1, strats['pair']))) else 1
    else: strats['finished'] = 1
    save_strat(strats)

if __name__ == "__main__":
    json_editor()












