from strategy import read_strat, save_strat
import time
import json
import keys
import requests
import datetime

# Import Youtube api stuff

STRATS = None
API = keys.key('youtube', 'api')
TITLE = []

def await_for_post(strats = None):
    """
    polling check for when Coin Bureau releases a video. Updates strats.json and ends as soon as video is published
    interval is sleep time between polling check
    """
    if strats==None: strats = read_strat()
    i = -1 #index for api accessing, looping through apis
    while strats['long'] == None:
        hour = datetime.datetime.now(datetime.timezone(datetime.timedelta(0))).hour
        if (hour==15 or hour == 16): interval = 0.3
        elif (hour >= 14 and hour <20): interval=0.5
        else: interval = 1
        time.sleep(interval)
        i = i+1 if i+1<len(API) else 0
        try: strats = check_post(strats, API[i])
        except: print(f"Error in checking YT with api [{i}] at time {get_current_time()}")
    return strats
    

def check_post(strats, api):
    """
    for Coin Bureau channel, checks if any new post within 1 minute included any mentions if specific key words and does not contain 'news'
    If so updates strats correctly and returns the strat. Else just returns the strat
    """
    title = get_latest_video_title(api)
    if 'news' in title: return strats

    for strat in strats['pair']:
        if strats['pair'][strat]['pos'] != 0: continue
        for keyword in strats['pair'][strat]['keywords']:
            if keyword in title:
                strats['long'] = strat
                save_strat(strats)

    return strats

def str_to_list(s):
    """
    Converts string title to list of words, removing anything except letters and numbers
    """
    def valid_character(c):
        return c.isalpha() or c==" " or c.isnumeric()
    return ''.join(filter(valid_character, s)).split()

def get_latest_video_title(api):
    """
    returns video title of the latest coin-bureau video

    For information: https://stackoverflow.com/questions/18953499/youtube-api-to-fetch-all-videos-on-a-channel
    answer by virtualmic
    """
    global TITLE
    url = f'https://www.googleapis.com/youtube/v3/playlistItems?playlistId=UUqK_GSMbpiV8spgD3ZGloSw&key={api}&part=snippet&maxResults=1'
    response = requests.get(url)
    title = response.json()['items'][0]['snippet']['title'].lower()
    if title != TITLE: 
        TITLE = title
        print(f"New video detected at: {get_current_time()}")
    return str_to_list(title)


def get_current_time():
    """
    returns the current time PDT as string
    """
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-8))).strftime("%H:%M:%S")

