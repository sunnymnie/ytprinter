import youtube_checker as yc
import requests
import json
import keys
import strategy
import os

def main():
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
