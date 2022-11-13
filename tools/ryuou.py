import re
import requests
from bs4 import BeautifulSoup
import time
import json
from logging import getLogger, config

def save_kif(crowurl, number):
    headers = {
    'User-Agent': 'shogi-kif-crawler(I am robot)'
    }
    url = "http://live.shogi.or.jp/ryuou/"
    
    res = requests.get(crowurl, headers = headers)
    
    soup = BeautifulSoup(res.text, "html.parser")
    elems = soup.find_all(href=re.compile("kifu/"))
    logger.info(crowurl)
    for e in elems:
        link = e.attrs["href"] # ex. "../kifu/27/ryuou201407010101.html"
        
        kif_name = (link.split("/")[-1]).split(".")[0] # ex. "ryuou201407010101"
        url_format = url+"kifu/"+str(number)+"/"+kif_name+".kif"
        urlData = requests.get(url_format).content
        with open('kifu/ryuou/'+kif_name+".kif", mode="wb") as f:
            f.write(urlData)
        logger.debug("saved: "+ kif_name+".kif")
        time.sleep(60)

if __name__ =='__main__':
    with open('log_config.json', 'r') as f:
        log_conf = json.load(f)
    config.dictConfig(log_conf)
    logger = getLogger(__name__)

    url = "http://live.shogi.or.jp/ryuou/"
    variant = ["7game.html", "tournament.html"]
    
    for i in range(25, 35):
        crowl_link = [
            url +  str(i) + "/" + variant[0],
            url +  str(i) + "/" + variant[1]
        ]
        
        save_kif(crowl_link[0], i)
        save_kif(crowl_link[1], i)
