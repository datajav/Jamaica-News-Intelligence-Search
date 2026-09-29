import requests

url = "https://uwispace.sta.uwi.edu/server/api/discover/search/objects"
params = {
    "query": "Jamaica",
    "scope": "",
    "f.entityType": "Publication,equals",
    "page": 0,
    "size": 5
}

resp = requests.get(url, timeout=20)
print(resp.status_code)
print(resp.text[:1000])