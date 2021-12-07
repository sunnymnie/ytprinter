import youtube_checker as yc
import requests
import json
import keys
import strategy
import os
import random
import admin

def TEST_get_latest_video_title(api):
    print("WARNING: RUNNING TEST FUNCTION TEST_get_latest_video_title")
    num = random.randint(0, 3)
    if (num==0):
        return ['omegas', 'smega', 'deltex', 'betrix', 'asdfe']
    elif (num==1):
        return ['asdfew', 'vrsdafs', 'dfweft', 'dsafww3', 'g3q4fd', 'dfewddd', 'g4qddd', 'dfa32e']
    elif (num==2):
        return []
    else:
        return ['33qre', '33qre', 'dfsaewfe', 'veqggrd', 'dfwq23f', 'fda3w2e', 'dfdfd2']
            
def main():
    with open('strats1.json', 'w') as f:
        pass
def main2():
    strats = strategy.read_strat()
    print(os.path.isfile('strats.json'))
    strategy.save_strat(strats)

def main1():
    API = keys.key('youtube', 'api')
    for i in range(len(API)):
        api = API[i]
        url = f'https://www.googleapis.com/youtube/v3/playlistItems?playlistId=UUqK_GSMbpiV8spgD3ZGloSw&key={api}&part=snippet&maxResults=1'
        response = requests.get(url)
        print(f"======================================[{i}]=========================================")
        print(response.json())


if __name__ == "__main__":
    main()
else: print("WARNING: imported TEST module test.py")
