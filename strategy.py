import json
import os
import uuid
import critical_moment as cm

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
        cmd = input("Type [v] to view all strats, [a] to add strat, [d] to delete strat, [l] to edit leverage, [i] to init strats, [q] to quit\n")
        if (cmd.lower() == "v"): view_all_strats(strats)
        elif (cmd.lower() == "i"): init_strats(strats)
        elif (cmd.lower() == "a"): add_strat(strats)
        elif (cmd.lower() == "d"): delete_strat(strats)
        elif (cmd.lower() == "l"): edit_leverage(strats)
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
        print(f"{strat}: pos = {info['pos']}         leverage = {info['leverage']}         price = {info['price']}")
        print("Keywords:")
        for keyword in info['keywords']:
            print(f"- {keyword}")

        print("Critical moments:")
        for t in info['critical_moments']:
            print(cm.critical_moment_to_str(t))

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

    critical_moments = [] 
    while True:
        while True:
            crit = str(input(f"Choose {list(map(lambda x: x, cm.crit_dict))}. [h] to get definitions\n"))
            if crit == "h": print(list(map(lambda x: f"{x}: {cm.crit_dict[x].__name__}", cm.crit_dict)))
            elif cm.is_valid_criterion(crit): break
            else: print(f"{crit} is not a valid criterion. Valid criterions are {list(map(lambda x: x, cm.crit_dict))}")

        c_val = float(input(f"Input critical value. If price, input as percent (ie 1.02, 0.99), if time, input as seconds (ie 10000)\n"))
        amt = float(input("Input amount to liquidate. Enter input as float (ie 1 for all, 0.5 for half of remaining)\n"))

        triggers = []
        while True:
            print("Current triggers:")
            for t in triggers:
               print(cm.trigger_to_str(t))
            if input("[q] to quit, [] enter to add triggers\n")=="q": break

            while True:
                tcrit = str(input(f"Choose from {list(map(lambda x: x, cm.crit_dict))} for Critical Moment trigger. [h] to get definitions\n"))
                if tcrit == "h": print(list(map(lambda x: f"{x}: {cm.crit_dict[x].__name__}", cm.crit_dict)))
                elif cm.is_valid_criterion(tcrit): break
                else: print(f"{crit} is not a valid criterion. Valid criterions are {list(map(lambda x: x, cm.crit_dict))}")
            
            tc_val = float(input(f"Input critical value. If price, input as percent (ie 1.02, 0.99), if time, input as seconds (ie 10000)\n"))
            while True:
                func = str(input(f"Choose from {list(map(lambda x: x, cm.trig_dict))} for Trigger functions. [h] to get definitions\n"))
                if func == "h": print(list(map(lambda x: f"{x}: {cm.trig_dict[x].__name__}", cm.trig_dict)))
                elif cm.is_valid_func(func): break
                else: print(f"{func} is not a valid trigger function. Valid functions are {list(map(lambda x: x, cm.trig_dict))}")

            t = cm.new_trigger(tcrit, tc_val, func)
            triggers.append(t)
        
        critical_moments.append(cm.new_critical_moment(crit, c_val, amt, triggers))
        print(cm.critical_moment_to_str(critical_moments[-1]))
        if input("[q] to quit, [] enter to keep adding critical moments\n")=="q": break

     
    leverage = int(input("Enter int amount of leverage to use (default 20)\n"))

    strats['pair'][asset] = {'pos':0, 'price':None, 'time':None, 'leverage':leverage, 'keywords':keywords, 'critical_moments':critical_moments}
    strats['finished'] = 0
    save_strat(strats)
    print(f"{asset} strat successfully added")

def edit_leverage(strats):
    """
    prompts user to edit leverage allocated to margin portfolio
    """
    lev = float(input(f"Enter new amount of leverage. Current leverage: {strats['leverage']}\n"))
    strats['leverage'] = lev
    save_strat(strats)
    print(f"Leverage set successfully to {strats['leverage']}")


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












