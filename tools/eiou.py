import re
import requests
from bs4 import BeautifulSoup
import time
import json
from logging import getLogger, config

def save_kif():
    headers = {
    'User-Agent': 'shogi-kif-crawler(I am robot)'
    }
    url = "http://live.shogi.or.jp/eiou/"
    
    res = requests.get(url, headers = headers)
    
    soup = BeautifulSoup(res.text, "html.parser")
    elems = soup.find_all(href=re.compile("kifu/"))
    
    for e in elems:
        link = e.attrs["href"] # ex. "../kifu/27/ryuou201407010101.html"
        
        kif_name = (link.split("/")[-1]).split(".")[0] # ex. "ryuou201407010101"
        
        if "http" in link:
            url_format = link
        else:
            url_format = url + link
        
        url_format = url_format.replace("html", "kif")
        logger.info(url_format)

        
        urlData = requests.get(url_format).content
        with open('kifu/eiou/'+kif_name+".kif", mode="wb") as f:
            f.write(urlData)
        logger.debug("saved: "+ kif_name+".kif")
        time.sleep(60)

if __name__ =='__main__':
    with open('log_config.json', 'r') as f:
        log_conf = json.load(f)
    config.dictConfig(log_conf)
    logger = getLogger(__name__)

    save_kif()
