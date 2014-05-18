import json
import requests

def query_musicbrainz(uid="", fmt="json"):
    url = "http://musicbrainz.org/ws/2/artist/"
    params = {"inc": "url-rels",
              "fmt": "json"} 
    r = requests.get(url + uid, params=params)
    # print "requesting", r.url

    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        r.raise_for_status()