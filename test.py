import youtube_checker as yc
import requests
import json
import keys

API = keys.key('youtube', 'api')
api = API[3]
url = f'https://www.googleapis.com/youtube/v3/playlistItems?playlistId=UUqK_GSMbpiV8spgD3ZGloSw&key={api}&part=snippet&maxResults=1'
response = requests.get(url)
print(response.json())
