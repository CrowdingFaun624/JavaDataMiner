'''Use `web_request` to take data from a url.'''

import requests
import time

REQUEST_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-ch-ua": "\"Google Chrome\";v=\"105\", \"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"105\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1"
}

def web_request(url:str, mode:str="t") -> str|bytes|dict:
    '''Returns content from a url. `mode` can be "t" for text, "b" for binary, or "j" for json'''
    if mode not in ("t", "b", "j"): raise ValueError
    for i in range(16):
        try:
            r = requests.get(url, headers=REQUEST_HEADERS)
            break  
        except requests.exceptions.ConnectionError:
            time.sleep(0.25)
    if mode == "t": return r.text
    elif mode == "b": return r.content
    elif mode == "j": return r.json()