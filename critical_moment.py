def new_critical_moment(criterion, c_val, amt, triggers=[]):
    _assert_valid_criterion(criterion) 
    return {"criterion":criterion, "c_val":c_val, "amt":amt, "active":1, "triggers":triggers}

## CRITERIONs for critical moment
def time_greater_than(price, time, new_price, new_time, c_val):
    return new_time > time + c_val

def price_greater_than(price, time, new_price, new_time, c_val):
    return new_price > price * c_val

def price_less_than(price, time, new_price, new_time, c_val):
    return new_price < price * c_val

crit_dict = {
    "tgt":time_greater_than,
    "pgt":price_greater_than,
    "plt":price_less_than
}

def new_trigger(criterion, c_val, func):
    _assert_valid_criterion(criterion) 
    _assert_valid_func(func)
    return {"criterion":criterion, "c_val":c_val, "func":func, "active":1}

def _assert_valid_criterion(criterion):
    if criterion not in crit_dict:
        raise ValueError("No valid criterion")

def _assert_valid_func(func):
    if func not in trig_dict:
        raise ValueError("No valid trigger function")

def is_valid_criterion(criterion):
    try: 
        _assert_valid_criterion(criterion)
        return True
    except:
        return False

def is_valid_func(func):
    try: 
        _assert_valid_func(func)
        return True
    except:
        return False
# CRITERIONS for triggers

def trigger_break_even(price, time, now_price, now_time, trigger, cm):
    cm["c_val"] = 1
    trigger['active'] = 0

def trigger_trailing_take_profit(price, time, now_price, now_time, trigger, cm):
    """Requires critical moment to be price less than"""
    amt = trigger['c_val'] - cm['c_val']
    cm["c_val"] += amt
    trigger['c_val'] += 0.01

trig_dict = {
    "be":trigger_break_even,
    "ttp":trigger_trailing_take_profit
}

def trigger_to_str(t):
    if t['active']:
        return f"{crit_dict[t['criterion']].__name__} {t['c_val']} --> {trig_dict[t['func']].__name__}"
    return f"{crit_dict[t['criterion']].__name__} {t['c_val']} --> {trig_dict[t['func']].__name__} (inactive)"

def critical_moment_to_str(c):
    m = f"{crit_dict[c['criterion']].__name__} {c['c_val']} --> liquidate {c['amt']}\n"
    for t in c['triggers']:
        m += f"   -{trigger_to_str(t)}\n"
    return m

