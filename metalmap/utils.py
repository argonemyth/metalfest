import json
import requests

def query_musicbrainz(uid="", fmt="json"):
    url = "http://musicbrainz.org/ws/2/artist/"
    params = {"inc": "url-rels",
              "fmt": "json"} 
    # musicbrainz wants meaning header
    # http://musicbrainz.org/doc/XML_Web_Service/Rate_Limiting
    headers = {
        'User-Agent': 'MetalMap/0.5',
        'From': 'hello@metalmap.com'  # This is another valid field
    }

    r = requests.get(url + uid, headers=headers, params=params)
    # print "requesting", r.url

    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        r.raise_for_status()