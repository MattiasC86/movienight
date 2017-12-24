import requests
import json


def get_by_title(title_input):
    payload = {'t': title_input, 'r': 'json', 'plot': 'short'}

    r = requests.get("http://www.omdbapi.com/?apikey=c803bcbf&", params=payload)

    result = r.json()
    return result


def search_by_title(title_input):
    payload = {'s': title_input, 'r': 'json', 'plot': 'short', 'type': 'movie'}

    r = requests.get("http://www.omdbapi.com/?apikey=c803bcbf&", params=payload)

    result = r.json()['Search']
    result = result[:8]

    return result
